#!/usr/bin/env python3
"""
GitHub to Codeberg/Forgejo Automated Migration & Sync Engine
Pure Python standard library implementation.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import http.server
import threading

class CodebergMigrator:
    def __init__(self, github_owner, github_repo, codeberg_token=None, base_gh_url="https://api.github.com", base_cb_url="https://codeberg.org/api/v1"):
        self.github_owner = github_owner
        self.github_repo = github_repo
        self.codeberg_token = codeberg_token
        self.base_gh_url = base_gh_url.rstrip('/')
        self.base_cb_url = base_cb_url.rstrip('/')

    def fetch_github_metadata(self):
        url = f"{self.base_gh_url}/repos/{self.github_owner}/{self.github_repo}"
        req = urllib.request.Request(url, headers={"User-Agent": "CodebergMigrator/1.0"})
        with urllib.request.urlopen(req) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
            raise RuntimeError(f"GitHub API Error: HTTP {resp.status}")

    def prepare_migration_payload(self, gh_meta, target_name=None):
        return {
            "clone_addr": gh_meta.get("clone_url"),
            "repo_name": target_name or gh_meta.get("name"),
            "private": gh_meta.get("private", False),
            "description": gh_meta.get("description", ""),
            "mirror": True,
            "wiki": gh_meta.get("has_wiki", True),
            "issues": gh_meta.get("has_issues", True)
        }

    def execute_migration(self, payload):
        url = f"{self.base_cb_url}/repos/migrate"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CodebergMigrator/1.0"
        }
        if self.codeberg_token:
            headers["Authorization"] = f"token {self.codeberg_token}"

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))

def run_self_test():
    print("[SELF-TEST] Initializing local mock server for GitHub & Codeberg APIs...")
    
    class MockAPIHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if "/repos/testuser/testrepo" in self.path:
                payload = {
                    "name": "testrepo",
                    "full_name": "testuser/testrepo",
                    "private": False,
                    "description": "Mock repository for migration testing",
                    "clone_url": "https://github.com/testuser/testrepo.git",
                    "has_wiki": True,
                    "has_issues": True
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if "/repos/migrate" in self.path:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length).decode('utf-8'))
                response = {
                    "id": 101,
                    "name": body.get("repo_name"),
                    "owner": {"username": "testuser"},
                    "clone_url": f"https://codeberg.org/testuser/{body.get('repo_name')}.git",
                    "status": "migrated_successfully"
                }
                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()

    server = http.server.HTTPServer(('127.0.0.1', 0), MockAPIHandler)
    port = server.server_port
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        mock_url = f"http://127.0.0.1:{port}"
        migrator = CodebergMigrator("testuser", "testrepo", base_gh_url=mock_url, base_cb_url=mock_url)

        print("[SELF-TEST] 1. Fetching GitHub repository metadata...")
        meta = migrator.fetch_github_metadata()
        assert meta["name"] == "testrepo", "Failed to fetch repository metadata"

        print("[SELF-TEST] 2. Preparing migration payload...")
        payload = migrator.prepare_migration_payload(meta)
        assert payload["mirror"] is True, "Failed to build mirror payload"

        print("[SELF-TEST] 3. Executing migration via API...")
        result = migrator.execute_migration(payload)
        assert result["status"] == "migrated_successfully", "Migration execution failed"

        print("\nSELF-TEST PASSED: Migration engine successfully fetched, transformed, and submitted payload.")
    finally:
        server.shutdown()

def main():
    parser = argparse.ArgumentParser(description="GitHub to Codeberg/Forgejo Migration & Sync Tool")
    parser.add_argument("--github-repo", help="GitHub repository in format: owner/repo")
    parser.add_argument("--codeberg-token", help="Codeberg API access token")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-test suite")

    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        sys.exit(0)

    if not args.github_repo:
        parser.print_help()
        sys.exit(1)

    parts = args.github_repo.split('/')
    if len(parts) != 2:
        print("Error: --github-repo must be in format 'owner/repo'")
        sys.exit(1)

    migrator = CodebergMigrator(parts[0], parts[1], codeberg_token=args.codeberg_token)
    print(f"Fetching metadata for {args.github_repo}...")
    
    try:
        meta = migrator.fetch_github_metadata()
        payload = migrator.prepare_migration_payload(meta)
        
        if not args.codeberg_token:
            print("\n[DRY-RUN MODE] No Codeberg token supplied. Migration payload generated:")
            print(json.dumps(payload, indent=2))
        else:
            print("Submitting migration request to Codeberg...")
            result = migrator.execute_migration(payload)
            print("Migration Status:")
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error executing migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
