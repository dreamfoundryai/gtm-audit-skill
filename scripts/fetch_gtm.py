#!/usr/bin/env python3
"""
GTM API v2 Data Fetcher

Connects to Google Tag Manager API v2 and exports container configuration
(tags, triggers, variables) as JSON files for audit analysis.

Usage:
    python fetch_gtm.py --auth-only          # Just authenticate and verify
    python fetch_gtm.py                       # Interactive: pick account/container
    python fetch_gtm.py --account-id 123 --container-id 456
    python fetch_gtm.py --container-path "accounts/123/containers/456"
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/tagmanager.readonly"]
CREDENTIALS_DIR = Path.home() / ".config" / "gtm-audit"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "token.json"
OUTPUT_DIR = Path("/tmp/gtm-audit")


def get_credentials():
    """Authenticate via OAuth 2.0 with cached token support."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            if not CREDENTIALS_FILE.exists():
                print(f"ERROR: OAuth credentials not found at {CREDENTIALS_FILE}")
                print()
                print("Setup instructions:")
                print("1. Go to https://console.cloud.google.com/apis/credentials")
                print("2. Create OAuth 2.0 Client ID (Desktop application type)")
                print("3. Download the JSON file")
                print(f"4. Save it as: {CREDENTIALS_FILE}")
                print("5. Enable the Tag Manager API at:")
                print("   https://console.cloud.google.com/apis/library/tagmanager.googleapis.com")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(creds.to_json())

    return creds


def build_service(creds):
    """Build the GTM API v2 service."""
    return build("tagmanager", "v2", credentials=creds)


def list_accounts(service):
    """List all accessible GTM accounts."""
    response = service.accounts().list().execute()
    return response.get("account", [])


def list_containers(service, account_path):
    """List containers in an account."""
    response = service.accounts().containers().list(parent=account_path).execute()
    return response.get("container", [])


def get_default_workspace(service, container_path):
    """Get the default workspace for a container."""
    response = (
        service.accounts()
        .containers()
        .workspaces()
        .list(parent=container_path)
        .execute()
    )
    workspaces = response.get("workspace", [])

    # Prefer "Default Workspace" or the first one
    for ws in workspaces:
        if ws.get("name", "").lower() in ("default workspace", "default"):
            return ws
    return workspaces[0] if workspaces else None


def fetch_tags(service, workspace_path):
    """Fetch all tags in a workspace."""
    response = (
        service.accounts()
        .containers()
        .workspaces()
        .tags()
        .list(parent=workspace_path)
        .execute()
    )
    return response.get("tag", [])


def fetch_triggers(service, workspace_path):
    """Fetch all triggers in a workspace."""
    response = (
        service.accounts()
        .containers()
        .workspaces()
        .triggers()
        .list(parent=workspace_path)
        .execute()
    )
    return response.get("trigger", [])


def fetch_variables(service, workspace_path):
    """Fetch all variables in a workspace."""
    response = (
        service.accounts()
        .containers()
        .workspaces()
        .variables()
        .list(parent=workspace_path)
        .execute()
    )
    return response.get("variable", [])


def fetch_built_in_variables(service, workspace_path):
    """Fetch enabled built-in variables."""
    try:
        response = (
            service.accounts()
            .containers()
            .workspaces()
            .built_in_variables()
            .list(parent=workspace_path)
            .execute()
        )
        return response.get("builtInVariable", [])
    except HttpError:
        # Some containers may not have this enabled
        return []


def fetch_folders(service, workspace_path):
    """Fetch all folders in a workspace."""
    try:
        response = (
            service.accounts()
            .containers()
            .workspaces()
            .folders()
            .list(parent=workspace_path)
            .execute()
        )
        return response.get("folder", [])
    except HttpError:
        return []


def interactive_select(items, label, name_key="name", id_key=None):
    """Let user pick from a list interactively."""
    if not items:
        print(f"No {label} found.")
        sys.exit(1)

    if len(items) == 1:
        print(f"Auto-selected {label}: {items[0].get(name_key, 'Unknown')}")
        return items[0]

    print(f"\nAvailable {label}:")
    for i, item in enumerate(items, 1):
        name = item.get(name_key, "Unknown")
        extra = f" (ID: {item.get(id_key, 'N/A')})" if id_key else ""
        print(f"  {i}. {name}{extra}")

    while True:
        try:
            choice = int(input(f"\nSelect {label} (1-{len(items)}): "))
            if 1 <= choice <= len(items):
                return items[choice - 1]
        except (ValueError, EOFError):
            pass
        print("Invalid choice. Try again.")


def save_json(data, filename):
    """Save data as pretty-printed JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    filepath.write_text(json.dumps(data, indent=2, default=str))
    print(f"  Saved: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Fetch GTM container data for audit")
    parser.add_argument("--auth-only", action="store_true", help="Only authenticate")
    parser.add_argument("--account-id", help="GTM account ID")
    parser.add_argument("--container-id", help="GTM container ID")
    parser.add_argument("--container-path", help="Full container path")
    parser.add_argument("--workspace-id", help="Workspace ID (default: auto-detect)")
    args = parser.parse_args()

    # Authenticate
    print("Authenticating with Google Tag Manager API...")
    creds = get_credentials()
    service = build_service(creds)

    # Auth-only mode
    if args.auth_only:
        accounts = list_accounts(service)
        print(f"\nAuthentication successful! Found {len(accounts)} accessible account(s):")
        for acct in accounts:
            print(f"  - {acct.get('name', 'Unknown')} (ID: {acct.get('accountId', 'N/A')})")
        return

    # Select account
    if args.container_path:
        # Parse path like "accounts/123/containers/456"
        parts = args.container_path.strip("/").split("/")
        account_path = f"accounts/{parts[1]}"
        container_path = args.container_path
    elif args.account_id and args.container_id:
        account_path = f"accounts/{args.account_id}"
        container_path = f"accounts/{args.account_id}/containers/{args.container_id}"
    else:
        # Interactive selection
        accounts = list_accounts(service)
        account = interactive_select(accounts, "account", "name", "accountId")
        account_path = account["path"]

        containers = list_containers(service, account_path)
        container = interactive_select(containers, "container", "name", "containerId")
        container_path = container["path"]

    print(f"\nFetching data for container: {container_path}")

    # Get workspace
    if args.workspace_id:
        workspace_path = f"{container_path}/workspaces/{args.workspace_id}"
    else:
        workspace = get_default_workspace(service, container_path)
        if not workspace:
            print("ERROR: No workspaces found in this container.")
            sys.exit(1)
        workspace_path = workspace["path"]
        print(f"Using workspace: {workspace.get('name', 'Unknown')}")

    # Fetch all data
    print("\nFetching container data...")

    try:
        tags = fetch_tags(service, workspace_path)
        print(f"  Tags: {len(tags)}")
    except HttpError as e:
        print(f"  Tags: ERROR - {e}")
        tags = []

    try:
        triggers = fetch_triggers(service, workspace_path)
        print(f"  Triggers: {len(triggers)}")
    except HttpError as e:
        print(f"  Triggers: ERROR - {e}")
        triggers = []

    try:
        variables = fetch_variables(service, workspace_path)
        print(f"  Variables: {len(variables)}")
    except HttpError as e:
        print(f"  Variables: ERROR - {e}")
        variables = []

    try:
        built_in_vars = fetch_built_in_variables(service, workspace_path)
        print(f"  Built-in Variables: {len(built_in_vars)}")
    except HttpError as e:
        print(f"  Built-in Variables: ERROR - {e}")
        built_in_vars = []

    try:
        folders = fetch_folders(service, workspace_path)
        print(f"  Folders: {len(folders)}")
    except HttpError as e:
        print(f"  Folders: ERROR - {e}")
        folders = []

    # Save to JSON files
    print("\nSaving data...")
    save_json(tags, "tags.json")
    save_json(triggers, "triggers.json")
    save_json(variables, "variables.json")
    save_json(built_in_vars, "built_in_variables.json")
    save_json(folders, "folders.json")

    metadata = {
        "container_path": container_path,
        "workspace_path": workspace_path,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "tags": len(tags),
            "triggers": len(triggers),
            "variables": len(variables),
            "built_in_variables": len(built_in_vars),
            "folders": len(folders),
        },
    }
    save_json(metadata, "metadata.json")

    print(f"\nDone! All data saved to {OUTPUT_DIR}/")
    print(f"Total: {len(tags)} tags, {len(triggers)} triggers, {len(variables)} variables")


if __name__ == "__main__":
    main()
