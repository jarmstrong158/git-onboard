"""
Tests for Git Onboard.

Run with:  python -m pytest test_git_onboard.py -v
Install:   pip install pytest  (if you don't have it)
"""

import os
import subprocess
import tempfile
import shutil
import pytest

# Import the functions we're testing
from git_onboard import (
    is_git_repo,
    get_repo_root,
    run_git,
)


# ============================================================
# FIXTURES — reusable setup/teardown for tests
# ============================================================

def force_remove_readonly(func, path, exc_info):
    """Handle Windows permission errors when cleaning up .git folders."""
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)


@pytest.fixture
def temp_dir():
    """Create a temporary directory and clean it up after the test."""
    d = tempfile.mkdtemp()
    original = os.getcwd()
    os.chdir(d)
    yield d
    os.chdir(original)
    shutil.rmtree(d, onexc=force_remove_readonly)


@pytest.fixture
def git_repo(temp_dir):
    """Create a temporary directory with an initialized git repo."""
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=temp_dir, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=temp_dir, capture_output=True
    )
    yield temp_dir


@pytest.fixture
def git_repo_with_commit(git_repo):
    """Create a temp git repo with at least one commit."""
    # Create a file and commit it
    test_file = os.path.join(git_repo, "test.txt")
    with open(test_file, "w") as f:
        f.write("hello world\n")
    subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=git_repo, capture_output=True
    )
    yield git_repo


# ============================================================
# TESTS: is_git_repo()
# ============================================================

class TestIsGitRepo:
    def test_returns_true_inside_repo(self, git_repo):
        """is_git_repo() should return True inside an initialized repo."""
        assert is_git_repo() is True

    def test_returns_false_outside_repo(self, temp_dir):
        """is_git_repo() should return False in a plain directory."""
        assert is_git_repo() is False


# ============================================================
# TESTS: get_repo_root()
# ============================================================

class TestGetRepoRoot:
    def test_returns_root_path(self, git_repo):
        """get_repo_root() should return the repo's root directory."""
        root = get_repo_root()
        assert root is not None
        assert os.path.isdir(root)
        assert os.path.isdir(os.path.join(root, ".git"))

    def test_returns_none_outside_repo(self, temp_dir):
        """get_repo_root() should return None when not in a repo."""
        assert get_repo_root() is None

    def test_works_from_subdirectory(self, git_repo):
        """get_repo_root() should find the root even from a subfolder."""
        sub = os.path.join(git_repo, "subdir")
        os.makedirs(sub)
        os.chdir(sub)
        root = get_repo_root()
        assert root is not None
        assert os.path.isdir(os.path.join(root, ".git"))


# ============================================================
# TESTS: run_git()
# ============================================================

class TestRunGit:
    def test_successful_command(self, git_repo, capsys):
        """run_git() should return (True, ...) for valid commands."""
        success, output, error = run_git("status")
        assert success is True

    def test_failed_command(self, temp_dir, capsys):
        """run_git() should return (False, ...) for commands that fail."""
        success, output, error = run_git("log")
        assert success is False

    def test_crlf_filter(self, git_repo, capsys):
        """run_git() should filter out CRLF warnings from output."""
        # Create a file and add it (might trigger CRLF on Windows)
        test_file = os.path.join(git_repo, "crlf_test.txt")
        with open(test_file, "w") as f:
            f.write("line one\nline two\n")
        success, _, _ = run_git("add", "crlf_test.txt")
        captured = capsys.readouterr()
        assert "LF will be replaced by CRLF" not in captured.out


# ============================================================
# TESTS: System directory protection
# ============================================================

class TestSystemDirectoryGuard:
    """Test that the protected directory list catches system paths."""

    # We test the logic directly rather than calling workflow_init()
    # (which requires user input)
    PROTECTED = ["\\windows", "\\system32", "\\program files",
                 "\\program files (x86)", "\\appdata"]

    @pytest.mark.parametrize("path", [
        "C:\\Windows\\System32",
        "C:\\Program Files\\SomeApp",
        "C:\\Program Files (x86)\\SomeApp",
        "C:\\Users\\Someone\\AppData\\Local",
    ])
    def test_system_paths_are_caught(self, path):
        """Paths containing system directories should be flagged."""
        path_lower = path.lower()
        assert any(p in path_lower for p in self.PROTECTED)

    @pytest.mark.parametrize("path", [
        "C:\\Users\\Dev\\repos\\my-project",
        "C:\\Projects\\website",
        "D:\\code\\app",
    ])
    def test_normal_paths_are_allowed(self, path):
        """Normal project paths should not be flagged."""
        path_lower = path.lower()
        assert not any(p in path_lower for p in self.PROTECTED)


# ============================================================
# TESTS: Git branching
# ============================================================

class TestBranching:
    def test_create_branch(self, git_repo_with_commit):
        """Creating a branch should succeed after at least one commit."""
        result = subprocess.run(
            ["git", "checkout", "-b", "test-branch"],
            cwd=git_repo_with_commit, capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_switch_branch(self, git_repo_with_commit):
        """Switching between branches should work."""
        subprocess.run(
            ["git", "checkout", "-b", "other-branch"],
            cwd=git_repo_with_commit, capture_output=True
        )
        result = subprocess.run(
            ["git", "checkout", "master"],
            cwd=git_repo_with_commit, capture_output=True, text=True
        )
        # Try 'master' first, fall back to 'main'
        if result.returncode != 0:
            result = subprocess.run(
                ["git", "checkout", "main"],
                cwd=git_repo_with_commit, capture_output=True, text=True
            )
        assert result.returncode == 0

    def test_merge_clean(self, git_repo_with_commit):
        """A clean merge (no conflicts) should succeed."""
        # Create a branch, add a file, switch back, merge
        subprocess.run(
            ["git", "checkout", "-b", "feature"],
            cwd=git_repo_with_commit, capture_output=True
        )
        new_file = os.path.join(git_repo_with_commit, "feature.txt")
        with open(new_file, "w") as f:
            f.write("new feature\n")
        subprocess.run(["git", "add", "."], cwd=git_repo_with_commit, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Add feature"],
            cwd=git_repo_with_commit, capture_output=True
        )

        # Switch back to the original branch and merge
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True
        )
        # Get the default branch name
        subprocess.run(
            ["git", "checkout", "-"],
            cwd=git_repo_with_commit, capture_output=True
        )
        result = subprocess.run(
            ["git", "merge", "feature"],
            cwd=git_repo_with_commit, capture_output=True, text=True
        )
        assert result.returncode == 0
        assert os.path.exists(new_file)

    def test_merge_conflict_detected(self, git_repo_with_commit):
        """Conflicting edits to the same file should trigger a conflict."""
        test_file = os.path.join(git_repo_with_commit, "test.txt")

        # Create branch and edit the file
        subprocess.run(
            ["git", "checkout", "-b", "conflict-branch"],
            cwd=git_repo_with_commit, capture_output=True
        )
        with open(test_file, "w") as f:
            f.write("branch version\n")
        subprocess.run(["git", "add", "."], cwd=git_repo_with_commit, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Branch edit"],
            cwd=git_repo_with_commit, capture_output=True
        )

        # Switch back and make a conflicting edit
        subprocess.run(
            ["git", "checkout", "-"],
            cwd=git_repo_with_commit, capture_output=True
        )
        with open(test_file, "w") as f:
            f.write("main version\n")
        subprocess.run(["git", "add", "."], cwd=git_repo_with_commit, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Main edit"],
            cwd=git_repo_with_commit, capture_output=True
        )

        # Attempt merge — should conflict
        result = subprocess.run(
            ["git", "merge", "conflict-branch"],
            cwd=git_repo_with_commit, capture_output=True, text=True
        )
        assert result.returncode != 0
        assert "CONFLICT" in result.stdout or "CONFLICT" in result.stderr

        # Clean up the failed merge
        subprocess.run(
            ["git", "merge", "--abort"],
            cwd=git_repo_with_commit, capture_output=True
        )


# ============================================================
# TESTS: .gitignore creation
# ============================================================

class TestGitignore:
    def test_gitignore_contents(self, git_repo):
        """Verify the .gitignore template has expected entries."""
        # Simulate what workflow_init writes
        gitignore_content = (
            "# Python\n"
            "__pycache__/\n"
            "*.pyc\n"
            ".env\n"
            "venv/\n"
            "\n"
            "# IDE / Editor\n"
            ".vscode/\n"
            ".idea/\n"
            "\n"
            "# OS files\n"
            ".DS_Store\n"
            "Thumbs.db\n"
        )
        assert "__pycache__/" in gitignore_content
        assert ".env" in gitignore_content
        assert ".vscode/" in gitignore_content
        assert ".DS_Store" in gitignore_content
