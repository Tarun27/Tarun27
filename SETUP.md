# Setup

Only `README.md` renders on the profile page. Everything else here exists to
keep it current.

| File | Role |
| --- | --- |
| `README.md` | The profile. Two generated blocks, everything else hand-written. |
| `profile.yml` | Window, cap, and the hide list. Rarely needs touching. |
| `scripts/update_stats.py` | Queries the GitHub GraphQL API and rewrites the two blocks. |
| `.github/workflows/update-stats.yml` | Runs the script daily at 02:17 UTC and on demand. |

## 1. The repository has to be `Tarun27/Tarun27`

A profile README only renders on your profile page if it lives in a public
repository named exactly after your username. Same name, same case.

## 2. Create the PAT

Settings → Developer settings → Personal access tokens.

**Classic token** — grant exactly:

- `repo` — needed to count private repositories and read their language bytes.
  The workflow only ever reads them; nothing is written back to those repos.
- `read:user` — needed for `contributionsCollection`.

**Fine-grained token** — set Repository access to *All repositories*, then
Repository permissions → Contents: **Read-only**, Metadata: **Read-only**.
Account permissions has no contribution scope, so if the commit counts come
back empty use a classic token.

Set an expiry you will actually notice. When it lapses the workflow fails loudly
rather than publishing zeros, so a dead token shows up as a red run, not a
silently wrong page.

## 3. Add it as a secret

Repo → Settings → Secrets and variables → Actions → New repository secret.

- Name: `STATS_TOKEN` — the script reads this exact name.
- Value: the token.

The default `GITHUB_TOKEN` cannot see private repositories, which is the whole
point of the workflow. It will not work here.

## 4. First run

Actions tab → **Update profile stats** → Run workflow. Until it succeeds, both
generated blocks say so in plain text — there are no placeholder numbers that
could ship as real ones.

## Keeping the projects block current

Nothing to maintain. The workflow lists every owned, non-fork repository pushed
to inside `projects.active_days` (60), most recent first, capped at
`max_entries`. Push to a repo and it appears; go quiet for two months and it
drops off.

Each line's one-liner is **the repository's own GitHub description**. Set it on
the repo itself — the About box, top right of the repo page — and it shows up
here on the next run. A repo with no description renders as a bare name, and the
workflow log says how many are in that state.

Private repositories are listed by name and marked `private`; public ones link
to the source. To keep a repository's name off the page entirely, add it to
`projects.hide` in `profile.yml`.

## Local run

```sh
pip install pyyaml
STATS_TOKEN=ghp_... GITHUB_LOGIN=Tarun27 python scripts/update_stats.py
```

## Before this goes public

- Replace `REPLACE-ME` in the README footer with your LinkedIn handle.
- Add GitHub descriptions to any repo you want described on the page.
