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
        os.chdir(path)
        explain(f"""This folder is already a Git repo. No need to init again.
  Path: {path}

  This tool is now pointed at that folder. All menu options
  will work against this repo.""")
        return

    # Run git init in the target directory
    original_dir = os.getcwd()
    os.chdir(path)
    success, _, _ = run_git("init")

    if not success:
        os.chdir(original_dir)

    if success:
        # Stay in the repo directory so all other options work against it
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

  This tool is now pointed at that folder, so all the other
  menu options (status, commit, push, etc.) will work against
  the repo you just created. No need to navigate there yourself.

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
  Option 7. Clone a repo — download someone else's project
  Option 8. Create a branch — work on changes without affecting main
  Option 9. Merge branches — combine branch changes back together""")
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
    results = input("  Results — what does this make easier, faster, or less frustrating?\n  > ").strip()
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
# WORKFLOW: Create a new branch
# ============================================================

def workflow_branch():
    explain("""--- Create a New Branch ---

WHAT IS A BRANCH?
  A branch is a separate copy of your project where you can make
  changes without affecting the original. Think of it like this:

    Main road (your 'main' or 'master' branch)
      └── Side road (your new branch)

  You drive down the side road, build something, and if it works
  out, you merge it back onto the main road. If it doesn't work
  out, you can abandon the side road and the main road is untouched.

WHY USE BRANCHES?
  - Test new ideas without breaking what already works
  - Work on multiple features at the same time
  - Keep your 'main' branch clean and always working
  - This is how professional teams work — nobody codes
    directly on 'main' in the real world""")

    input("  Press Enter to continue...")
    clear_screen()

    if not is_git_repo():
        explain("You're not inside a Git repository. Use 'Initialize a new repo' first.")
        return

    # Check for commits first — can't branch without at least one
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        explain("""You need at least one commit before you can create a branch.
Go to option 3 (Stage and commit) first, then come back here.""")
        return

    print("  1. Create a new branch")
    print("  2. Switch to an existing branch")
    print("  3. See all branches")
    print("  4. Return to main menu")
    print()

    while True:
        try:
            choice = int(input("  Pick an option: ").strip())
            if 1 <= choice <= 4:
                break
        except ValueError:
            pass
        print("  Please enter 1, 2, 3, or 4.")

    if choice == 4:
        print("  Cancelled.")
        return

    if choice == 3:
        explain("""Listing all branches. The one with the * is the branch
you're currently on:""")
        run_git("branch")
        return

    if choice == 2:
        # Show existing branches first
        explain("Here are your current branches:")
        run_git("branch")

        branch_name = input("  Enter the branch name to switch to: ").strip()
        if not branch_name:
            print("  Cancelled.")
            return

        explain(f"""Switching to branch '{branch_name}':

WHAT THIS DOES:
  'git checkout' moves you from your current branch to another one.
  All your files will update to match whatever state that branch is
  in. Don't worry — nothing is lost. Your other branch still exists
  and you can switch back anytime.""")

        success, _, stderr = run_git("checkout", branch_name)

        if success:
            explain(f"""You're now on branch '{branch_name}'.

Any changes you make from here will only affect THIS branch.
Your other branches are untouched.""")
        elif "did not match" in (stderr or ""):
            explain(f"""Branch '{branch_name}' doesn't exist. Check the spelling
and try again — branch names are case-sensitive.

Tip: use option 3 (See all branches) to see what's available.""")
        return

    # choice == 1: Create new branch
    clear_screen()
    explain("""--- Name Your New Branch ---

Branch names should be short, descriptive, and use hyphens instead
of spaces. Good naming helps you (and your team) know what each
branch is for at a glance.

GOOD EXAMPLES:
  add-login-page
  fix-search-bug
  update-readme

BAD EXAMPLES:
  my branch        (no spaces allowed)
  asdf             (tells you nothing)
  final-v2-real    (we've all been there, but don't)""")

    branch_name = input("  Enter a name for your new branch: ").strip()

    if not branch_name:
        print("  Cancelled.")
        return

    # Validate branch name (no spaces)
    if " " in branch_name:
        explain("Branch names can't have spaces. Use hyphens instead (e.g., 'my-feature').")
        return

    explain(f"""Creating branch '{branch_name}' and switching to it:

WHAT THIS DOES:
  'git checkout -b' does two things at once:
    1. Creates a new branch (a copy of your current branch)
    2. Switches you onto it immediately

  From this point on, any changes you make only affect this branch.
  Your main branch stays exactly how it was.""")

    success, _, _ = run_git("checkout", "-b", branch_name)

    if success:
        explain(f"""Branch '{branch_name}' created! You're now working on it.

WHAT TO DO NEXT:
  1. Make your changes (edit files, add features, fix bugs)
  2. Use option 3 (Stage and commit) to save your work on this branch
  3. When you're happy with the changes, use option 9 (Merge branches)
     to bring them back into your main branch

  You can switch back to your main branch at any time using
  option 8 → Switch to an existing branch.

  Your main branch is completely untouched until you merge.""")


# ============================================================
# WORKFLOW: Merge branches
# ============================================================

def workflow_merge():
    explain("""--- Merge Branches ---

WHAT IS MERGING?
  Merging takes the changes from one branch and combines them into
  another. It's how you bring your work back to the main road after
  building something on a side road.

  Example:
    You created a branch called 'add-login-page', built the login
    page, and committed your work. Now you want those changes on
    your main branch. That's a merge.

HOW IT WORKS:
  1. You switch to the branch you want to RECEIVE the changes
     (usually 'main' or 'master')
  2. You tell Git to merge the other branch INTO it
  3. Git combines the changes automatically

WHAT COULD GO WRONG?
  If both branches edited the SAME lines in the SAME file, Git
  can't decide which version to keep. That's called a 'merge
  conflict.' Don't panic — this tool will walk you through
  fixing it if that happens.""")

    input("  Press Enter to continue...")
    clear_screen()

    if not is_git_repo():
        explain("You're not inside a Git repository. Use 'Initialize a new repo' first.")
        return

    # Show current branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True, text=True
    )
    current_branch = result.stdout.strip()

    explain(f"""You are currently on branch: {current_branch}

Here are all your branches:""")
    run_git("branch")

    # Check if there's more than one branch
    all_branches = subprocess.run(
        ["git", "branch"],
        capture_output=True, text=True
    )
    branch_list = [b.strip().lstrip("* ") for b in all_branches.stdout.strip().splitlines()]

    if len(branch_list) < 2:
        explain("""You only have one branch. There's nothing to merge.

Create a new branch first using option 8 (Create a new branch),
make some changes, commit them, and then come back here to merge.""")
        return

    # Step 1: Switch to the receiving branch
    explain(f"""--- Merge: Step 1 of 2 — SWITCH TO THE RECEIVING BRANCH ---

You need to be on the branch that should RECEIVE the changes.
Usually that's your main branch ('main' or 'master').

You're currently on: {current_branch}""")

    target = input("  Switch to which branch? (or press Enter to stay on current): ").strip()

    if target and target != current_branch:
        explain(f"Switching to '{target}':")
        success, _, _ = run_git("checkout", target)
        if not success:
            explain("Failed to switch branches. Check the name and try again.")
            return
        current_branch = target

    # Step 2: Pick the branch to merge in
    input("\n  Press Enter to continue...")
    clear_screen()

    explain(f"""--- Merge: Step 2 of 2 — MERGE THE OTHER BRANCH ---

You're on: {current_branch}

Now pick which branch to merge INTO '{current_branch}'.
This will bring all the changes from that branch into this one.""")

    # Show branches (excluding current)
    other_branches = [b for b in branch_list if b != current_branch]
    print()
    for i, b in enumerate(other_branches, 1):
        print(f"  {i}. {b}")
    print()

    while True:
        try:
            choice = int(input("  Pick a branch to merge (number): ").strip())
            if 1 <= choice <= len(other_branches):
                break
        except ValueError:
            pass
        print(f"  Please enter a number between 1 and {len(other_branches)}.")

    merge_branch = other_branches[choice - 1]

    explain(f"""Merging '{merge_branch}' into '{current_branch}':

WHAT'S ABOUT TO HAPPEN:
  Git will try to combine all the commits from '{merge_branch}'
  into '{current_branch}'. If there are no conflicting edits,
  it will happen automatically.""")

    success, output, stderr = run_git("merge", merge_branch)

    if success:
        explain(f"""Merge complete! The changes from '{merge_branch}' are now
part of '{current_branch}'.

WHAT TO DO NEXT:
  - Use option 5 (Push to GitHub) to upload the merged changes
  - If you're done with the '{merge_branch}' branch, you can
    delete it (it's safe — all its changes are here now)""")

        if prompt_yes_no(f"Delete the '{merge_branch}' branch? (it's been merged, so it's safe)"):
            run_git("branch", "-d", merge_branch)
            explain(f"Branch '{merge_branch}' deleted. Clean and tidy.")

    elif "CONFLICT" in (output or "") or "CONFLICT" in (stderr or ""):
        # Merge conflict! Walk them through it.
        handle_merge_conflict(merge_branch, current_branch)
    else:
        explain(f"""Merge failed. Here's what Git said:

  {stderr or output or 'No details available.'}

This sometimes happens if you have uncommitted changes. Try:
  1. Go to option 3 (Stage and commit) to save your current work
  2. Come back and try the merge again""")


def handle_merge_conflict(merge_branch, current_branch):
    """Walk the user through resolving a merge conflict."""
    explain(f"""--- MERGE CONFLICT ---

Don't panic. This is normal and every developer deals with it.

WHAT HAPPENED:
  Both '{current_branch}' and '{merge_branch}' edited the same
  lines in the same file(s). Git doesn't know which version you
  want to keep, so it's asking YOU to decide.

WHAT GIT DID:
  Git marked the conflicting sections in your files with special
  markers that look like this:

  <<<<<<< HEAD
  (your version on '{current_branch}')
  =======
  (their version from '{merge_branch}')
  >>>>>>> {merge_branch}

  Everything between <<<<<<< and ======= is YOUR current version.
  Everything between ======= and >>>>>>> is the INCOMING version.

LET'S SEE WHICH FILES HAVE CONFLICTS:""")

    run_git("status", "--short")

    explain("""Files marked with 'UU' or 'AA' have conflicts that need fixing.

HOW TO FIX IT:
  1. Open each conflicted file in your text editor
  2. Find the <<<<<<< / ======= / >>>>>>> markers
  3. Decide which version to keep (or combine them)
  4. DELETE the marker lines (<<<, ===, >>>) entirely
  5. Save the file

EXAMPLE — before fixing:
  <<<<<<< HEAD
  print("Hello World")
  =======
  print("Hello, World!")
  >>>>>>> add-greeting

EXAMPLE — after fixing (you picked the version you want):
  print("Hello, World!")

  (You deleted the markers and kept the version you preferred.)""")

    input("  Press Enter when you've fixed the conflicts in your editor...")
    clear_screen()

    explain("""Now let's verify the conflicts are resolved.

IMPORTANT: Make sure you've:
  - Removed ALL <<<<<<< / ======= / >>>>>>> markers
  - Saved every conflicted file
  - The files look the way you want them to

Let's check the status:""")

    run_git("status", "--short")

    # Check if there are still unmerged files
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True
    )
    has_conflicts = any(
        line.startswith("UU") or line.startswith("AA")
        for line in result.stdout.strip().splitlines()
    )

    if has_conflicts:
        explain("""It looks like there are still unresolved conflicts.

Open the files marked with 'UU' in your editor and make sure
you've removed ALL the conflict markers (<<<, ===, >>>).

When you're done, come back and try the merge again.""")
        return

    explain("""Looks good! Now we need to:
  1. Stage the resolved files (tell Git you've fixed them)
  2. Complete the merge with a commit""")

    if prompt_yes_no("Stage all resolved files and complete the merge?"):
        run_git("add", ".")

        success, _, _ = run_git("commit", "-m",
                                f"Merge branch '{merge_branch}' into {current_branch}")

        if success:
            explain(f"""Merge conflict resolved! The changes from '{merge_branch}'
are now part of '{current_branch}'.

You just handled a merge conflict like a pro. That's genuinely
one of the things that trips up even experienced developers.

WHAT TO DO NEXT:
  - Use option 5 (Push to GitHub) to upload the merged result
  - If you're done with '{merge_branch}', you can delete it""")

            if prompt_yes_no(f"Delete the '{merge_branch}' branch?"):
                run_git("branch", "-d", merge_branch)
                explain(f"Branch '{merge_branch}' deleted.")
    else:
        explain("""Merge left in progress. You can:
  - Fix more files and come back to complete it
  - Or run 'git merge --abort' to cancel the merge entirely""")

        if prompt_yes_no("Cancel the merge entirely?"):
            run_git("merge", "--abort")
            explain("Merge cancelled. Everything is back to how it was before.")


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
    (
        "Create a new branch",
        "Work on changes in isolation without affecting your main code.",
        workflow_branch,
    ),
    (
        "Merge branches",
        "Combine changes from one branch into another. Handles conflicts too.",
        workflow_merge,
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
# SETUP: Git installation and configuration checks
# ============================================================

def check_git_installed():
    """
    Check if Git is installed. If not, walk the user through installation
    and wait for them to complete it before continuing.
    Returns True once Git is detected.
    """
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)

    if result.returncode == 0:
        return True

    # Git not found — walk the user through installation
    clear_screen()
    print()
    print("  ╔══════════════════════════════════╗")
    print("  ║       GIT ONBOARD — SETUP        ║")
    print("  ╚══════════════════════════════════╝")
    print()
    print("  Before we can start, you need Git installed on your")
    print("  computer. Git is the tool that tracks your files —")
    print("  this program is just a friendly wrapper around it.")
    print()
    print("  Don't worry, it's free and takes about 2 minutes.")
    print()

    if os.name == "nt":
        # Windows
        print("  ── HOW TO INSTALL GIT (WINDOWS) ──────────────────────")
        print()
        print("  1. Open your browser and go to:")
        print("     https://git-scm.com/downloads/win")
        print()
        print("  2. The download should start automatically.")
        print("     If not, click the download link for your system")
        print("     (most likely '64-bit Git for Windows Setup')")
        print()
        print("  3. Run the installer. You'll see MANY screens of")
        print("     options — just click 'Next' on every screen.")
        print("     The defaults are fine.")
        print()
        print("  4. Click 'Install', then 'Finish' when it's done")
        print()
        print("  5. IMPORTANT: After installing, you need to CLOSE")
        print("     this terminal window and open a new one. Then")
        print("     run this program again. The new terminal will")
        print("     know where Git is; this one won't.")
    else:
        # macOS / Linux
        print("  ── HOW TO INSTALL GIT ─────────────────────────────────")
        print()
        print("  1. Open your browser and go to:")
        print("     https://git-scm.com/downloads")
        print()
        print("  2. Pick your operating system (macOS or Linux)")
        print()
        print("  3. Follow the installation instructions on the page")
        print()
        print("  4. Close this terminal and open a new one, then")
        print("     run this program again")

    print()
    print("  ─────────────────────────────────────────────────────────")
    print()
    input("  Press Enter to exit. Come back after installing Git...")
    sys.exit(0)


def check_git_config():
    """
    Check if git user.name and user.email are configured.
    If not, walk the user through setting them up.
    These are required before making any commits.
    """
    name_result = subprocess.run(
        ["git", "config", "--global", "user.name"],
        capture_output=True, text=True
    )
    email_result = subprocess.run(
        ["git", "config", "--global", "user.email"],
        capture_output=True, text=True
    )

    name = name_result.stdout.strip()
    email = email_result.stdout.strip()

    if name and email:
        return  # Already configured

    clear_screen()
    print()
    print("  ── GIT IDENTITY SETUP ─────────────────────────────────")
    print()
    print("  Git needs to know who you are. Every commit (save point)")
    print("  you make gets tagged with your name and email so people")
    print("  can see who wrote the code.")
    print()
    print("  This is a one-time setup. You won't be asked again.")
    print()

    if not name:
        while True:
            name = input("  Enter your name (e.g., Jane Smith): ").strip()
            if name:
                break
            print("  Name can't be empty.")

        subprocess.run(["git", "config", "--global", "user.name", name])
        print(f"  Set: user.name = {name}")
        print()

    if not email:
        while True:
            email = input("  Enter your email (use the same one as your GitHub account): ").strip()
            if email:
                break
            print("  Email can't be empty.")

        subprocess.run(["git", "config", "--global", "user.email", email])
        print(f"  Set: user.email = {email}")
        print()

    explain(f"""You're all set! Git will tag your commits as:
  {name} <{email}>

  You can change these later with:
    git config --global user.name "New Name"
    git config --global user.email "new@email.com" """)

    input("  Press Enter to continue...")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    clear_screen()

    # Step 1: Make sure Git is installed
    check_git_installed()

    # Step 2: Make sure Git identity is configured
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    print(f"\n  Git detected: {result.stdout.strip()}")
    check_git_config()

    # Step 3: Welcome and main menu
    show_welcome()
    main_menu()
