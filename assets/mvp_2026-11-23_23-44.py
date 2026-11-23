#!/usr/bin/env python3
"""
Git Repo Board - Micro-SaaS MVP Core
Scans local directories for Git repositories, checks their status/branches,
and serves an interactive web dashboard or outputs JSON analytics.

Zero external dependencies required (Pure Python standard library).
Supports '--self-test' flag for clean execution test.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler


def find_git_repos(root_dir):
    """Recursively search for Git repositories in root_dir."""
    git_repos = []
    for root, dirs, _ in os.walk(root_dir):
        if '.git' in dirs:
            git_repos.append(root)
            dirs.remove('.git')  # Do not search inside .git directory
    return git_repos


def get_repo_info(repo_path):
    """Gather status, branch, and commit details for a single Git repository."""
    def run_git(args):
        try:
            res = subprocess.run(
                ['git'] + args,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return res.stdout.strip()
        except Exception:
            return ""

    branch = run_git(['rev-parse', '--abbrev-ref', 'HEAD'])
    status = run_git(['status', '--porcelain'])
    last_commit = run_git(['log', '-1', '--format=%h - %s (%cr)'])

    is_dirty = len(status) > 0
    uncommitted_files = len(status.splitlines()) if is_dirty else 0

    return {
        "name": os.path.basename(os.path.abspath(repo_path)),
        "path": os.path.abspath(repo_path),
        "branch": branch or "unknown",
        "is_dirty": is_dirty,
        "uncommitted_files": uncommitted_files,
        "last_commit": last_commit or "No commits found"
    }


class DashboardRequestHandler(BaseHTTPRequestHandler):
    """Simple HTTP Server Handler serving JSON API and Dashboard GUI."""
    scan_directory = "."

    def do_GET(self):
        if self.path == "/api/repos":
            repos = find_git_repos(self.scan_directory)
            data = [get_repo_info(r) for r in repos]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Git Repo Board MVP</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 30px; background: #0f172a; color: #f8fafc; }
        h1 { color: #38bdf8; }
        .card { background: #1e293b; padding: 18px; margin: 12px 0; border-radius: 8px; border-left: 5px solid #22c55e; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .dirty { border-left-color: #ef4444; }
        .badge { background: #334155; padding: 4px 8px; border-radius: 4px; font-size: 12px; color: #cbd5e1; }
        .status-dirty { color: #fca5a5; font-weight: bold; }
        .status-clean { color: #86efac; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🚀 Git Repository Board</h1>
    <p>Monitoring active local Git workspace repositories.</p>
    <div id="repos">Loading repository status...</div>

    <script>
        fetch('/api/repos')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('repos');
                if (data.length === 0) {
                    container.innerHTML = '<p>No Git repositories detected in scanning folder.</p>';
                    return;
                }
                container.innerHTML = data.map(repo => `
                    <div class="card ${repo.is_dirty ? 'dirty' : ''}">
                        <h2>${repo.name} <span class="badge">${repo.branch}</span></h2>
                        <p><strong>Path:</strong> <code>${repo.path}</code></p>
                        <p><strong>Status:</strong> ${repo.is_dirty 
                            ? '<span class="status-dirty">⚠️ Uncommitted Changes (' + repo.uncommitted_files + ' modified file/s)</span>' 
                            : '<span class="status-clean">✅ Clean</span>'}</p>
                        <p><strong>Latest Commit:</strong> ${repo.last_commit}</p>
                    </div>
                `).join('');
            })
            .catch(err => {
                document.getElementById('repos').innerHTML = '<p style="color:red">Failed to fetch repo data.</p>';
            });
    </script>
</body>
</html>"""
            self.wfile.write(html.encode('utf-8'))


def run_self_test():
    """Execute isolated self-test using temporary directory without altering system."""
    print("=== STARTING SELF-TEST ===")
    
    # Verify git availability
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
    except Exception:
        print("[FAIL] Git CLI is not installed or not available in PATH.")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmpdir:
        test_repo = os.path.join(tmpdir, "test_repo")
        os.makedirs(test_repo)

        # 1. Initialize temporary Git repo
        subprocess.run(['git', 'init'], cwd=test_repo, capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Tester'], cwd=test_repo, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=test_repo, capture_output=True)

        # 2. Add file (dirty state check)
        sample_file = os.path.join(test_repo, "file.txt")
        with open(sample_file, "w") as f:
            f.write("Hello World")

        repos = find_git_repos(tmpdir)
        assert len(repos) == 1, f"Expected 1 repo, found {len(repos)}"

        info = get_repo_info(test_repo)
        assert info["name"] == "test_repo", "Repository name mismatch"
        assert info["is_dirty"] is True, "Dirty state not properly detected"
        assert info["uncommitted_files"] == 1, "Uncommitted count mismatch"

        # 3. Commit file (clean state check)
        subprocess.run(['git', 'add', '.'], cwd=test_repo, capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial test commit'], cwd=test_repo, capture_output=True, check=True)

        info_clean = get_repo_info(test_repo)
        assert info_clean["is_dirty"] is False, "Clean state not properly detected"
        assert "Initial test commit" in info_clean["last_commit"], "Commit message missing"

        print("[SUCCESS] All scanner assertions passed successfully!")
        print(f"Sample JSON Result:\n{json.dumps(info_clean, indent=2)}")

    print("=== SELF-TEST COMPLETED CLEANLY ===")


def main():
    parser = argparse.ArgumentParser(description="Git Repository Board - Developer Productivity MVP")
    parser.add_argument("--dir", default=".", help="Root directory to scan for Git repositories (default: current directory)")
    parser.add_argument("--port", type=int, default=8080, help="Web Server Port (default: 8080)")
    parser.add_argument("--json", action="store_true", help="Print JSON repo summary and exit")
    parser.add_argument("--self-test", action="store_true", help="Perform automated self-test and exit")

    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        sys.exit(0)

    if args.json:
        repos = find_git_repos(args.dir)
        result = [get_repo_info(r) for r in repos]
        print(json.dumps(result, indent=2))
        sys.exit(0)

    DashboardRequestHandler.scan_directory = args.dir
    server_address = ('', args.port)
    httpd = HTTPServer(server_address, DashboardRequestHandler)
    print(f"🚀 Git Repo Board server running at http://localhost:{args.port}")
    print(f"🔍 Scanning root directory: {os.path.abspath(args.dir)}")
    print("Press Ctrl+C to stop.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    main()
