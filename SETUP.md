# Setup

Only `README.md` renders on the profile page. Everything else here exists to
keep it current.

| File | Role |
| --- | --- |
| `README.md` | The profile. Two generated blocks, everything else hand-written. |
| `projects.yml` | Curated copy for the projects block. The only file to edit routinely. |
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

The workflow renders a project only when it appears in `projects.yml` *and* its
repo has been pushed to inside `settings.active_days` (60). Entries are ordered
most-recent-first and capped at `max_entries`. Nothing you have not written copy
for is ever named, so pushing to a private repo does not leak its name onto a
public page.

To add a project, add an entry. To retire one, delete it — or just stop pushing
to it and it ages out on its own.

If no repo has been pushed to inside the window, it falls back to the three most
recent so the section is never empty.

## Local run

```sh
pip install pyyaml
STATS_TOKEN=ghp_... GITHUB_LOGIN=Tarun27 python scripts/update_stats.py
```

## Before this goes public

- Replace `REPLACE-ME` in the README footer with your LinkedIn handle.
- Add the Play Store URL to the `byte-design` entry in `projects.yml`.
