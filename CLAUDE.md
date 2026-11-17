# CLAUDE.md

## What this is

A GitHub profile README repo (the special `<username>/<username>` repo). Only `README.md` renders on the
profile page. A small Python script refreshes two generated blocks in it from the GitHub GraphQL API, and a
scheduled GitHub Action runs that script and pushes the result to `main`. This repo is public: never put
personal data, tokens or secrets in any file.

## Stack

- Python 3.12 (the workflow's version), standard library plus `pyyaml`. No other dependencies.
- GitHub GraphQL API (`https://api.github.com/graphql`) called with `urllib`.
- GitHub Actions for scheduling. No build step, no package manifest.

## Layout

| Path | Role | Edited by |
| --- | --- | --- |
| `README.md` | The profile page. | Hand-written, except the two generated blocks below |
| `profile.yml` | Config for the projects block under `projects:` (`active_days`, `max_entries`, `fallback_entries`, `hide` list). | By hand, rarely |
| `scripts/update_stats.py` | Queries the API and rewrites the generated blocks in `README.md`. | By hand |
| `.github/workflows/update-stats.yml` | Runs the script on a schedule and pushes. | By hand |
| `SETUP.md` | One-time setup notes (repo naming, token scopes, secret, first run). | By hand |
| `github-profile-readme-prompt.md` | Local-only prompt used to create the profile. Git-ignored, may be absent. | Not tracked |
| `.gitignore` | Ignores `__pycache__/`, `*.pyc`, `.venv/`, `.claude/`, the prompt file. | By hand |

### Generated vs hand-edited

`README.md` has two generated blocks, delimited by marker comments:

- `<!-- SNAPSHOT:START -->` ... `<!-- SNAPSHOT:END -->` (repo counts, commit counts, top languages)
- `<!-- PROJECTS:START -->` ... `<!-- PROJECTS:END -->` (recently pushed repos)

Do not hand-edit anything between those markers; the next run overwrites it. Do not remove or rename the
markers: the script aborts if it cannot find them. Everything outside the markers is hand-written. Project
descriptions come from each repo's own GitHub description, so change them on that repo, not here.

## Running the script locally

Needs a classic personal access token (`repo` and `read:user` scopes). It calls the live GitHub API and
**rewrites `README.md` in place**, so only run it deliberately and review `git diff` afterwards.

```sh
pip install pyyaml
STATS_TOKEN=<token> GITHUB_LOGIN=<login> python3 scripts/update_stats.py
```

Env vars: `STATS_TOKEN` (required), `GITHUB_LOGIN` (required). The script exits non-zero with an
`error:` message if either is missing, or if the API response looks like a partial read (for example zero
private repos). It deliberately refuses to write rather than publish wrong numbers. There is no `--help`
or dry-run mode.

Safe check without a token: `python3 -m py_compile scripts/update_stats.py` (syntax only).

## How the workflow runs

`.github/workflows/update-stats.yml` ("Update profile stats"):

- Triggers: daily cron at 02:17 UTC, and manual `workflow_dispatch`.
- Uses the repo secret `STATS_TOKEN` (a PAT; the default `GITHUB_TOKEN` cannot see private repos) and sets
  `GITHUB_LOGIN` to the repo owner.
- Resets to the latest `origin/main`, runs the script, and if `README.md` changed, commits only
  `README.md` as `github-actions[bot]` and pushes to `main`. On a rejected push it re-renders on the new
  `main` (up to 3 attempts) rather than rebasing.
- `concurrency` group `update-stats` prevents overlapping runs.

## Tests

There are no tests yet and no test command. Verify changes with the syntax check above, and for script
changes a manual run against a real token (with the README diff reviewed before keeping it).

## Conventions

- The history is almost entirely bot commits with the message `chore: refresh profile stats`. Hand commits
  should use a short conventional prefix (`chore:`, `docs:`, `fix:`) with a one-line description.
- Commit straight to `main`; there is no PR flow. Pull before committing, since the bot pushes daily.
- Keep the script idempotent and fail-loud: add new guards that abort before writing, never fall back to
  placeholder numbers.
- Keep personal data (emails, tokens, private repo details beyond what the generated block already shows)
  out of every tracked file.
