#!/usr/bin/env python3
"""
Git Onboard — A Git learning companion.
Teaches Git by walking you through real commands with plain-English explanations.
"""

import subprocess
import sys
import os


# ============================================================
# UTILITIES
# These are the building blocks every workflow uses.
# ============================================================

def clear_screen():
    """Clear the terminal for a fresh view."""
    os.system("cls" if os.name == "nt" else "clear")


def explain(text):
    """Print an explanation block — visually distinct from commands and output."""
    print()
    for line in text.strip().splitlines():
        print(f"  {line}")
    print()


SEPARATOR = "  ────────────────────────────────────────────────────────────"


def run_git(*args):
    """
    Run a Git command via subprocess.
    Shows the actual command, a bridge explanation, the raw output
    inside visual separators, and returns the result.
    Returns (success: bool, stdout: str, stderr: str).
    """
    cmd = ["git"] + list(args)
    cmd_str = " ".join(cmd)

    print()
    print(f"  COMMAND RAN: {cmd_str}")
    print()
    print(f"  Below is the output you'd see if you typed '{cmd_str}'")
    print("  directly in your terminal. This is what Git is telling you:")
    print(SEPARATOR)

    result = subprocess.run(cmd, capture_output=True, text=True)

    output = result.stdout.strip()
    error = result.stderr.strip()

    # Filter out CRLF warnings — these are just Windows line-ending noise
    # that would confuse beginners. They're harmless and not actionable.
    if error:
        filtered_lines = [
            line for line in error.splitlines()
            if "LF will be replaced by CRLF" not in line
        ]
        error = "\n".join(filtered_lines).strip()

    if output:
        print(output)
    if error and result.returncode != 0:
        print(f"  ERROR: {error}")
    elif error:
        # Git sometimes writes non-error info to stderr (e.g., progress messages)
        print(error)

    if not output and not error:
        print("  (no output)")

    print(SEPARATOR)
    print()
    return result.returncode == 0, output, error


def prompt_yes_no(question):
    """Ask a yes/no question. Returns True for yes."""
    while True:
        answer = input(f"  {question} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please enter y or n.")


def is_git_repo():
    """Check if the current directory is inside a Git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True
    )
    return result.returncode == 0


# ============================================================
# WORKFLOW: Initialize a new repository
# ============================================================

def workflow_init():
    explain("""--- Initialize a New Repository ---

WHAT THIS DOES:
  'git init' creates a hidden .git folder in a project directory.
  (A "project directory" is just a regular folder on your computer —
  wherever your project files live. And "hidden" means your operating
  system doesn't show it by default, but it's still there. On Windows
  you can see hidden folders by clicking View > Show > Hidden items
  in File Explorer.)

  That .git folder is where Git stores all your version history —
  every save point (commit) you'll ever make lives in there. You
  never need to open or edit it directly. Git manages it for you.

  Think of it as telling Git: "Start watching this folder."

  Nothing gets uploaded anywhere. This is purely local — just Git
  setting up its tracking system on your machine.""")

    input("  Press Enter to continue...")
    clear_screen()

    print("  Enter the path to your project folder")
    print("  (the folder with the files you want to track)")
    path = input("  Press Enter to use the current directory: ").strip()

    if not path:
        path = os.getcwd()

    path = os.path.abspath(path)

    # Guard against system directories that will always fail
    protected = ["\\windows", "\\system32", "\\program files",
                 "\\program files (x86)", "\\appdata"]
    path_lower = path.lower()
    if any(p in path_lower for p in protected):
        explain(f"""That path looks like a system folder:
  {path}

  You can't (and shouldn't) init a Git repo in a system directory.
  You need to point this at YOUR project folder — for example:
    C:\\Users\\YourName\\repos\\my-project

  Go back and enter the path to where your actual project files live.""")
        return

    if not os.path.isdir(path):
        if prompt_yes_no(f"'{path}' doesn't exist. Create it?"):
            os.makedirs(path)
            print(f"  Created: {path}")
        else:
            print("  Cancelled.")
            return

    # Check if already a repo
    git_dir = os.path.join(path, ".git")
    if os.path.isdir(git_dir):
        explain(f"This folder is already a Git repo. No need to init again.\n  Path: {path}")
        return

    # Run git init in the target directory
    original_dir = os.getcwd()
    os.chdir(path)
    success, _, _ = run_git("init")
    os.chdir(original_dir)

    if success:
        # Offer to create a .gitignore so junk files don't get committed
        gitignore_path = os.path.join(path, ".gitignore")
        if not os.path.exists(gitignore_path):
            explain("""One more thing — a .gitignore file tells Git which files to
IGNORE (not track). Without one, Git will try to save everything
in this folder, including junk files like:
  - __pycache__/  (Python's auto-generated cache files)
  - .env          (secret keys and passwords)
  - node_modules/ (thousands of dependency files)

These clutter your repo and can even leak sensitive info.""")

            if prompt_yes_no("Create a .gitignore with common defaults?"):
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write(
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
                print(f"  Created: {gitignore_path}")
                print()

        explain(f"""Done! Git is now tracking: {path}

WHAT JUST HAPPENED:
  Git is watching this folder now, but ONLY on your machine.
  Nothing has been uploaded. GitHub doesn't know about this yet.

THE FULL FLOW:
  [done] Step 1. Initialize     — you just did this
   -->   Step 2. Check status    — see what Git sees (option 2)
         Step 3. Stage + commit  — save a snapshot locally (option 3)
         Step 4. Create a README — build your project's front page (option 4)
         Step 5. Push to GitHub  — upload everything (option 5)""")
    else:
        explain(f"""Git init failed for: {path}

  This usually means you don't have permission to create files in
  that folder. Make sure the path points to a folder YOU created —
  for example:
    C:\\Users\\YourName\\repos\\my-project

  Try again with the correct path to your project folder.""")


# ============================================================
# WORKFLOW: Check repository status
# ============================================================

def workflow_status():
    explain("""--- Check Repository Status ---

WHAT THIS DOES:
  'git status' shows you what's changed since your last commit (save point).

  You'll see files in three categories:
    - Staged:     Ready to be committed (in the box, ready to ship)
    - Modified:   Changed but not staged yet (you edited it but haven't
                  put it in the box)
    - Untracked:  Brand new files Git hasn't seen before""")

    input("  Press Enter to continue...")
    clear_screen()

    if not is_git_repo():
        explain("You're not inside a Git repository. Use 'Initialize a new repo' first.")
        return

    _, output, _ = run_git("status")

    # Interpret the output for the user
    if output:
        porcelain = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True
        )
        status_lines = porcelain.stdout.strip()

        if not status_lines:
            explain("""WHAT THIS MEANS:
  Everything is clean — all your files match your last save point.
  There's nothing new to commit right now.""")
        else:
            has_untracked = any(line.startswith("?") for line in status_lines.splitlines())
            has_modified = any(line[1] == "M" for line in status_lines.splitlines() if len(line) > 1)
            has_staged = any(line[0] in "MADRC" for line in status_lines.splitlines() if len(line) > 0)

            explain("WHAT THIS MEANS:")
            if has_untracked:
                print("  - Files listed as 'Untracked' are new files Git can see but")
                print("    hasn't saved yet.")
            if has_modified:
                print("  - Files listed as 'Modified' have been edited since your last")
                print("    save point but haven't been staged yet.")
            if has_staged:
                print("  - Files listed as 'Staged' are ready to be committed (saved).")

            explain("""WHAT TO DO NEXT:
  To save these changes, use option 3 (Stage and commit) from the
  main menu. That will lock them into a snapshot on your machine.
  Then use option 4 (Create a README) to build your project's front
  page, and option 5 (Push to GitHub) to upload everything.""")


# ============================================================
# WORKFLOW: Stage and commit changes
# ============================================================

def workflow_stage_commit():
    explain("""--- Stage and Commit Changes ---

WHAT THIS DOES:
  This is a two-step process:

  1. STAGE (git add):  Pick which changes to include in your next save.
     Think of it as putting items into a box.

  2. COMMIT (git commit):  Seal the box with a label describing what's
     inside. This creates a permanent save point in your history.

  You can't commit without staging first — Git needs you to be
  intentional about what goes into each save point.""")

    input("  Press Enter to continue...")
    clear_screen()

    if not is_git_repo():
        explain("You're not inside a Git repository. Use 'Initialize a new repo' first.")
        return

    # Show current status
    explain("""--- Stage and Commit: Step 1 of 2 — STAGING ---

First, let's see what files Git has noticed. The output below
uses shorthand symbols:
  ??  = Untracked (a new file Git hasn't saved before)
  M   = Modified  (a file that changed since your last save)
  A   = Staged    (a file already marked for the next save)""")

    run_git("status", "--short")

    # Check if there's anything to commit
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )

    if not result.stdout.strip():
        explain("Nothing to commit — your working directory is clean. Make some changes first!")
        return

    # Stage
    explain("""Now you need to pick which of those files to include in your
next save point. You can stage all of them at once, or pick
specific files. For now, staging everything is usually the
right call.""")

    print("  1. Stage all changes")
    print("  2. Stage specific files")
    print("  3. Return to main menu")
    print()

    while True:
        try:
            choice = int(input("  Pick an option: ").strip())
            if 1 <= choice <= 3:
                break
        except ValueError:
            pass
        print("  Please enter 1, 2, or 3.")

    if choice == 3:
        print("  Cancelled.")
        return

    if choice == 1:
        explain("Staging all changes:")
        run_git("add", ".")
    else:
        file_path = input("  Enter the file name (or path) to stage: ").strip()
        if file_path:
            explain(f"Staging '{file_path}':")
            run_git("add", file_path)
        else:
            print("  No file specified. Cancelled.")
            return

    # Show what's staged
    input("\n  Press Enter to continue...")
    clear_screen()

    explain("""--- Stage and Commit: Step 2 of 2 — COMMITTING ---

Here's what's staged and ready to be saved:""")
    run_git("status", "--short")

    explain("""Now you need a commit message — a short label describing what
this save point contains. Good messages describe WHAT changed
and WHY.

Examples:
  "Add player health bar to HUD"
  "Fix login bug where empty password was accepted"
  "Initial commit — project scaffolding" """)

    message = input("  Enter your commit message: ").strip()

    if not message:
        print("  No message entered. Cancelled.")
        return

    explain("Creating commit:")
    success, _, _ = run_git("commit", "-m", message)

    if success:
        explain("""Commit created!

WHAT JUST HAPPENED:
  Your changes are saved, but ONLY on your machine. GitHub still
  doesn't have them yet.

THE FULL FLOW:
  [done] Step 1. Initialize     — already done
  [done] Step 2. Check status    — already done
  [done] Step 3. Stage + commit  — you just did this
   -->   Step 4. Create a README — build your project's front page (option 4)
                                   (skip if you already have one)
         Step 5. Push to GitHub  — upload everything (option 5)""")


# ============================================================
# WORKFLOW: Push to GitHub
# ============================================================

def workflow_push():
    explain("""--- Push to GitHub ---

WHAT THIS DOES:
  Right now, your project and its save history only exist on your
  computer. If your hard drive dies, it's gone.

  'git push' uploads your local commits (save points) to GitHub,
  which stores a copy of your project online. This does two things:
    1. Backs up your work to the cloud
    2. Makes it visible on your GitHub profile (so employers,
       collaborators, or anyone else can see it)

  Think of it as syncing your local saves to an online backup.""")

    input("  Press Enter to continue...")
    clear_screen()

    if not is_git_repo():
        explain("You're not inside a Git repository. Use 'Initialize a new repo' first.")
        return

    # Check if user has a GitHub account
    explain("""Before we push, you need a GitHub account. If you already
have one, skip ahead. If not, let's set one up now.""")

    print("  1. I already have a GitHub account")
    print("  2. I need to create one")
    print("  3. Return to main menu")
    print()

    while True:
        try:
            acct_choice = int(input("  Pick an option: ").strip())
            if 1 <= acct_choice <= 3:
                break
        except ValueError:
            pass
        print("  Please enter 1, 2, or 3.")

    if acct_choice == 3:
        print("  Cancelled.")
        return

    if acct_choice == 2:
        clear_screen()
        explain("""--- Setting Up a GitHub Account ---

GitHub is free. Here's how to create an account:

  1. Open your browser and go to: github.com
  2. Click the "Sign up" button (top right)
  3. Enter your email address and create a password
  4. Choose a username — this will be your public identity
     (tip: keep it professional. Employers will see this.
     Something like your name or initials works well.)
  5. Complete the verification steps (CAPTCHA, email confirm)
  6. When asked about preferences, you can skip the
     personalization — it doesn't affect anything

Once your account is created and you're signed in,
come back here and press Enter to continue.""")

        input("  Press Enter when your GitHub account is ready...")
        clear_screen()

    # Check if remote exists
    result = subprocess.run(
        ["git", "remote", "-v"],
        capture_output=True, text=True
    )

    if not result.stdout.strip():
        explain("""--- Push: Step 1 of 2 — CONNECT TO GITHUB ---

Your local repo doesn't know where to upload to yet. You need
to create a repo on GitHub and then tell your local repo:
"when I say push, send it HERE."

That connection is called a 'remote'. The first one you set up
is always named 'origin' — that's just the default name Git
uses. Think of it as 'the original place this uploads to.'
You only set this up once per project.

HERE'S WHAT TO DO:
  1. Open your browser and go to: github.com/new
     (you must already be signed into GitHub for this to work)
  2. Under "Repository name", type the name of your project
     (tip: match your folder name to keep things clean)
  3. Leave it set to "Public" (so employers can see your work)
  4. DO NOT check any boxes under "Initialize this repository"
     (no README, no .gitignore, no license — we handle that)
  5. Click the green "Create repository" button
  6. You'll see a setup page — look for a URL near the top
     that looks like: https://github.com/yourname/your-repo.git
  7. Copy that URL and paste it below""")

        url = input("  Enter the GitHub repo URL (or press Enter to cancel): ").strip()

        if not url:
            print("  Cancelled.")
            return

        input("\n  Press Enter to continue...")
        clear_screen()

        explain("""--- Push: Step 2 of 2 — LINKING AND UPLOADING ---

Now we'll do two things:
  1. Tell your local repo where to upload (linking the remote)
  2. Push your commits up to GitHub

Linking to GitHub:""")
        success, _, _ = run_git("remote", "add", "origin", url)

        if not success:
            explain("Failed to add remote. Check the URL and try again.")
            return
    else:
        explain("--- Pushing to GitHub ---\n\nRemote is already connected:")
        print(result.stdout)
        print()

    # Check which branch we're on
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True
    )
    branch = result.stdout.strip() or "main"

    explain(f"Uploading your commits to GitHub (branch: {branch}):")
    success, _, stderr = run_git("push", "-u", "origin", branch)

    if success:
        explain("""Done! Your code is now live on GitHub.

WHAT JUST HAPPENED:
  Your local commits have been uploaded to your GitHub repo.
  Anyone with the link can now see your project, your code,
  and your README.

THE FULL FLOW:
  [done] Step 1. Initialize     — already done
  [done] Step 2. Check status    — already done
  [done] Step 3. Stage + commit  — already done
  [done] Step 4. Create a README — already done
  [done] Step 5. Push to GitHub  — you just did this!

  You're all set. From now on, whenever you make changes:
  just repeat steps 2, 3, and 5 (status → commit → push).

EXTRA TOOLS (explore these when you need them):
  Option 6. View commit history — look back at past saves
  Option 7. Clone a repo — download someone else's project""")
    elif "src refspec" in (stderr or ""):
        explain("""Push failed because there's nothing to push yet — you
haven't made any commits (save points) in this repo.

WHAT TO DO:
  Go back to the main menu and use option 3 (Stage and commit)
  to save your files first. Then come back here and push again.""")
    elif "rejected" in (stderr or ""):
        explain("""Push was rejected. This usually means GitHub has files that
your local repo doesn't know about. The most common cause:
you checked 'Add a README' when creating the repo on GitHub.

QUICKEST FIX:
  1. Go to your repo page on GitHub
  2. Click Settings (tab at the top) → scroll to the bottom
  3. Delete the repository
  4. Recreate it at github.com/new — this time DON'T check
     any of the boxes under 'Initialize this repository'
  5. Come back here and try Push again""")
    elif "Authentication" in (stderr or "") or "fatal: could not read" in (stderr or ""):
        explain("""Push failed. This is most likely an authentication issue —
GitHub needs to know who you are before it lets you upload.

WHAT TO DO:
  A browser window may have opened asking you to sign in to
  GitHub. Follow the prompts to log in with your GitHub
  account.

  If no window opened, you may need to set up authentication
  manually. The easiest way on Windows:
    1. Open a regular terminal (not this tool)
    2. Use 'cd' to navigate to your project folder first, e.g.:
       cd C:\\Users\\YourName\\repos\\your-project
    3. Type: git push -u origin main
    4. A login prompt or browser window should appear
    5. Sign in with your GitHub credentials
    6. Come back here — future pushes should work automatically""")
    else:
        explain(f"""Push failed with an unexpected error. Here's what Git said:

  {stderr or 'No error details available.'}

If you're not sure what this means, try these steps:
  1. Go back to the main menu
  2. Use option 2 (Check status) to see your repo's state
  3. Make sure you've committed (option 3) before pushing
  4. Try pushing again""")


# ============================================================
# WORKFLOW: View commit history
# ============================================================

def workflow_log():
    explain("""--- View Commit History ---

WHAT THIS DOES:
  'git log' shows your past commits (save points) in reverse order
  — newest first. Each entry shows:
    - A unique ID (hash) — Git's fingerprint for that save
    - Who made it
    - When
    - The commit message

  Think of it as a timeline of every save you've ever made.""")

    input("  Press Enter to continue...")
    clear_screen()

    if not is_git_repo():
        explain("You're not inside a Git repository. Use 'Initialize a new repo' first.")
        return

    # Check if there are any commits
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        explain("No commits yet. Make your first commit using 'Stage and commit changes.'")
        return

    explain("Showing recent commits (last 10):")
    run_git("log", "--oneline", "--graph", "-10")


# ============================================================
# WORKFLOW: Clone a repository
# ============================================================

def workflow_clone():
    explain("""--- Clone a Repository ---

WHAT THIS DOES:
  'git clone' downloads a complete copy of a repository from GitHub
  (or any Git host) to your machine. You get all the files AND the
  full version history.

  This is how you grab someone else's project, or pull down your
  own repo onto a new machine.""")

    input("  Press Enter to continue...")
    clear_screen()

    url = input("  Enter the repo URL to clone: ").strip()

    if not url:
        print("  No URL entered. Cancelled.")
        return

    dest = input("  Clone into which folder? (press Enter for current directory): ").strip()

    if dest:
        explain(f"Cloning into '{dest}':")
        run_git("clone", url, dest)
    else:
        explain("Cloning:")
        run_git("clone", url)

    explain("""If that succeeded, you now have a full copy of the repo.
Use your terminal to navigate into the new folder to start working with it.""")


# ============================================================
# WORKFLOW: Create a README
# ============================================================

def get_repo_root():
    """Find the root directory of the current Git repo, or None."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def workflow_readme():
    explain("""--- Create a README ---

WHAT THIS DOES:
  The README.md is the front page of your project on GitHub.
  It's the first thing recruiters, hiring managers, and other
  developers see when they visit your repo.

  This walks you through creating one that tells the STORY
  of your project — not just what it does, but what problem
  it solves and what impact it had.

  Format: Markdown (.md) — a simple text formatting language
  that GitHub renders into nice-looking pages.""")

    input("  Press Enter to continue...")
    clear_screen()

    # Find the repo root so the README lands in the right place
    repo_root = get_repo_root()
    if not repo_root:
        explain("""You're not inside a Git repository. Use 'Initialize a new repo'
first (option 1), then come back here to create your README.""")
        return

    print("  Answer the following prompts. Press Enter to skip any section.\n")

    project_name = input("  Project name: ").strip()
    tagline = input("  One-line description: ").strip()
    problem = input("  The Problem — what inefficiency/gap/need existed?\n  > ").strip()
    solution = input("  The Solution — what does this tool/project do?\n  > ").strip()
    how_it_works = input("  How It Works — high-level architecture (2-3 sentences):\n  > ").strip()
    results = input("  Results — measurable impact (hours saved, $ saved, etc.):\n  > ").strip()
    tech = input("  Tech Stack — languages, libraries, APIs:\n  > ").strip()
    status = input("  Status (Active / Complete / In Progress): ").strip()

    # Build the README content
    lines = []
    lines.append(f"# {project_name or 'Project Name'}")

    if tagline:
        lines.append(f"\n{tagline}")

    if problem:
        lines.append(f"\n## The Problem\n\n{problem}")

    if solution:
        lines.append(f"\n## The Solution\n\n{solution}")

    if how_it_works:
        lines.append(f"\n## How It Works\n\n{how_it_works}")

    if results:
        lines.append(f"\n## Results\n\n{results}")

    if tech:
        lines.append(f"\n## Tech Stack\n\n{tech}")

    if status:
        lines.append(f"\n## Status\n\n{status}")

    readme_content = "\n".join(lines) + "\n"

    # Preview
    print("\n  --- README Preview ---\n")
    for line in readme_content.splitlines():
        print(f"    {line}")
    print()

    if prompt_yes_no("Write this to README.md?"):
        file_path = os.path.join(repo_root, "README.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        explain(f"""README.md created at: {file_path}

THE FULL FLOW:
  [done] Step 1. Initialize     — already done
  [done] Step 2. Check status    — already done
  [done] Step 3. Stage + commit  — already done
  [done] Step 4. Create a README — you just did this
   -->   Step 5. Push to GitHub  — upload everything (option 5)

  BEFORE YOU PUSH: Go back to option 3 (Stage and commit) to save
  the README into your repo history. Then use option 5 to push.""")
    else:
        print("  Cancelled. Nothing was written.")


# ============================================================
# MAIN MENU
# ============================================================

MENU_OPTIONS = [
    (
        "Initialize a new repo",
        "Set up Git tracking in a project folder. This is always the first step.",
        workflow_init,
    ),
    (
        "Check status",
        "See what files have changed since your last save point.",
        workflow_status,
    ),
    (
        "Stage and commit changes",
        "Select changes and save a snapshot with a descriptive label.",
        workflow_stage_commit,
    ),
    (
        "Create a README",
        "Build the front page of your project — the first thing people see on GitHub.",
        workflow_readme,
    ),
    (
        "Push to GitHub",
        "Upload your saved snapshots to your GitHub profile for the world to see.",
        workflow_push,
    ),
    (
        "View commit history",
        "See a timeline of every snapshot you've saved.",
        workflow_log,
    ),
    (
        "Clone a repo",
        "Download an existing project from GitHub to your machine.",
        workflow_clone,
    ),
]


def show_welcome():
    """First-launch welcome screen. Explains Git, GitHub, and this tool."""
    clear_screen()
    print()
    print("  ╔══════════════════════════════════╗")
    print("  ║       WELCOME TO GIT ONBOARD     ║")
    print("  ╚══════════════════════════════════╝")
    print()
    print("  Before we start, let's cover the basics.")
    print()
    print("  ── WHAT IS GIT? ──────────────────────────────────────────────")
    print()
    print("  Git is a version control system. Think of it as an unlimited")
    print("  'undo history' for your entire project. Every time you save a")
    print("  snapshot (called a 'commit'), Git remembers exactly what every")
    print("  file looked like at that moment.")
    print()
    print("  You can go back to any snapshot, see what changed between")
    print("  them, and never worry about losing your work again.")
    print()
    print("  ── WHAT IS GITHUB? ───────────────────────────────────────────")
    print()
    print("  GitHub is a website that stores your Git snapshots online.")
    print("  It's where developers share code, collaborate, and build")
    print("  portfolios that show off their work to employers.")
    print()
    print("  Git is the tool on your computer. GitHub is the cloud backup.")
    print("  You use Git locally, then 'push' your work up to GitHub")
    print("  when you're ready to share it.")
    print()
    print("  ── WHAT DOES THIS TOOL DO? ───────────────────────────────────")
    print()
    print("  Git Onboard walks you through Git step by step. Before every")
    print("  action, it explains what's about to happen and why. After")
    print("  every action, it shows you the real Git command that ran.")
    print()
    print("  The goal: you learn Git by using it, not by memorizing")
    print("  commands. Eventually, you won't need this tool at all.")
    print()
    input("  Press Enter to continue...")


def main_menu():
    """Display the main menu and handle user input."""
    while True:
        clear_screen()
        print()
        print("  ╔══════════════════════════════════╗")
        print("  ║         GIT ONBOARD              ║")
        print("  ║   Your Git learning companion    ║")
        print("  ╚══════════════════════════════════╝")
        print()
        print("  ── WHAT DO I DO? ─────────────────────────────────────────")
        print("  The options below are listed in the order you'd typically")
        print("  use them. If this is your first time, start with #1 and")
        print("  work your way down as you go.")
        print()
        print("  ── OPTIONS ───────────────────────────────────────────────")
        print()

        for i, (label, description, _) in enumerate(MENU_OPTIONS, 1):
            marker = " ← start here" if i == 1 else ""
            print(f"  {i}. {label}{marker}")
            print(f"     {description}")
            print()

        exit_num = len(MENU_OPTIONS) + 1
        print(f"  {exit_num}. Exit")
        print()

        try:
            choice = int(input("  Pick an option: ").strip())
        except (ValueError, EOFError):
            print("  Please enter a number.")
            continue

        if choice == exit_num:
            print("\n  See you next time. Keep committing.\n")
            break

        if 1 <= choice <= len(MENU_OPTIONS):
            clear_screen()
            try:
                MENU_OPTIONS[choice - 1][2]()
            except KeyboardInterrupt:
                print("\n  Interrupted. Returning to menu.")
        else:
            print(f"  Please enter a number between 1 and {exit_num}.")

        input("\n  Press Enter to return to the menu...")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    clear_screen()

    # Verify Git is available
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print()
        print("  Git is not installed or not found on your system.")
        print("  You need Git before this tool can do anything.")
        print()
        print("  HOW TO INSTALL:")
        print("    1. Go to https://git-scm.com/downloads")
        print("    2. Download the installer for your operating system")
        print("    3. Run the installer (the default settings are fine)")
        print("    4. Close and reopen your terminal")
        print("    5. Run this program again")
        print()
        sys.exit(1)

    print(f"\n  Git detected: {result.stdout.strip()}")
    show_welcome()
    main_menu()
