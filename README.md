# Git Onboard

A Python CLI tool that walks beginners through Git step by step — explaining what each command does, why it matters, and running the real commands for you.

## The Problem

Learning Git from scratch is intimidating. The commands are cryptic, the terminology is confusing, and most tutorials either assume prior knowledge or dump a wall of text without letting you actually do anything. Beginners end up copy-pasting commands they don't understand, and the first time something goes wrong (a merge conflict, a failed push, a detached HEAD), they're stuck with no idea how to fix it.

## The Solution

Git Onboard sits between you and Git. Before every command, it explains what's about to happen and why. After every command, it shows you the real output and interprets it in plain English. You learn by doing — not by memorizing.

It covers the full workflow: initializing a repo, staging and committing, creating a README, pushing to GitHub, branching, merging, and resolving merge conflicts. Built-in guardrails catch common beginner mistakes (wrong directory, missing commits, auth failures) before they become frustrating dead ends.

## How It Works

Runs in the terminal as a single Python script. On first launch, it checks for Git installation and walks you through setup if needed. Then it presents a numbered menu that follows the natural Git workflow — start at step 1 and work your way down. Designed to be used repeatedly until you're comfortable working with Git on your own.

## Getting Started

**Requirements:** Python 3.6+ and Git installed on your machine.

```
git clone https://github.com/jarmstrong158/git-onboard.git
cd git-onboard
python git_onboard.py
```

Or download the standalone `.exe` from the [Releases](https://github.com/jarmstrong158/git-onboard/releases) page (Windows, no Python required).

## Running Tests

```
pip install pytest
python -m pytest test_git_onboard.py -v
```

## Building from Source

To build a standalone `.exe` (no Python required for the end user):

```
pip install pyinstaller
pyinstaller --onefile git_onboard.py
```

The executable will be in the `dist/` folder.

## Tech Stack

Python, subprocess, Git CLI

## Status

Active
