#!/usr/bin/env python3
"""Regenerate the SNAPSHOT and PROJECTS blocks in README.md from the GitHub API.

Reads every owned, non-fork repository (public and private) via GraphQL, so the
numbers reflect all the work rather than the public slice of it. Requires a PAT
in STATS_TOKEN with `repo` scope — the default GITHUB_TOKEN cannot see private
repositories.

Fails loudly. A snapshot claiming zero private repositories is worse than a
stale one, so anything that looks like a partial read aborts before writing.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

API = "https://api.github.com/graphql"
ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CONFIG = ROOT / "profile.yml"

# Markup and config languages crowd out the ones that say something about the
# work. Bytes of HTML are not a signal about what someone builds.
LANGUAGE_IGNORE = {
    "HTML", "CSS", "SCSS", "Less", "Jupyter Notebook", "Makefile",
    "Dockerfile", "Roff", "Batchfile", "Procfile", "Vim Script", "TeX",
}
TOP_LANGUAGES = 4


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def graphql(token: str, query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    request = urllib.request.Request(
        API,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "profile-stats-updater",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        fail(f"GitHub API returned HTTP {exc.code}: {exc.read().decode()[:500]}")
    except urllib.error.URLError as exc:
        fail(f"could not reach the GitHub API: {exc.reason}")

    if "errors" in body:
        fail(f"GraphQL errors: {json.dumps(body['errors'])}")
    # data can be present-but-null on a partial failure, so do not chain .get()
    # off it — that crashes with an AttributeError instead of saying why.
    user = (body.get("data") or {}).get("user")
    if not user:
        fail(
            "GraphQL response contained no user. Check that STATS_TOKEN is a valid, "
            f"unexpired token and that the login is right (got {variables.get('login')!r})."
        )
    return user


COUNTS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    all:     repositories(ownerAffiliations: OWNER, isFork: false) { totalCount }
    public:  repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC)  { totalCount }
    private: repositories(ownerAffiliations: OWNER, isFork: false, privacy: PRIVATE) { totalCount }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      restrictedContributionsCount
    }
  }
}
"""

WINDOW_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      restrictedContributionsCount
    }
  }
}
"""

CALENDAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { totalContributions }
    }
  }
}
"""

REPOS_QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        pushedAt
        isPrivate
        url
        description
        primaryLanguage { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def iso(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def commits(collection: dict) -> int:
    """Commits including those in private repos.

    restrictedContributionsCount is what GitHub reports for contributions it
    will not itemise — the private ones. That is the number this whole page
    exists to surface, so it counts.
    """
    return (
        collection["totalCommitContributions"]
        + collection["restrictedContributionsCount"]
    )


def all_time_contributions(token: str, login: str, created_at: str) -> tuple[int, int]:
    """Total contributions since the account was created, and that start year.

    contributionsCollection caps its window at one year, so this walks the
    account year by year and sums. Cheap enough for a daily cron.
    """
    start = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    total = 0
    cursor = start
    while cursor < now:
        end = min(cursor + timedelta(days=365), now)
        user = graphql(token, CALENDAR_QUERY, {
            "login": login, "from": iso(cursor), "to": iso(end),
        })
        total += user["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        cursor = end
    return total, start.year


def fetch_repositories(token: str, login: str) -> list[dict]:
    repos: list[dict] = []
    cursor = None
    while True:
        user = graphql(token, REPOS_QUERY, {"login": login, "cursor": cursor})
        page = user["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return repos
        cursor = page["pageInfo"]["endCursor"]


def top_languages(repos: list[dict]) -> list[str]:
    totals: dict[str, int] = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in LANGUAGE_IGNORE:
                continue
            totals[name] = totals.get(name, 0) + edge["size"]
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return [name for name, _ in ranked[:TOP_LANGUAGES]]


def render_snapshot(
    counts: dict, year: int, month: int, languages: list[str],
    all_time: int, since: int,
) -> str:
    repos = counts["all"]["totalCount"]
    public = counts["public"]["totalCount"]
    private = counts["private"]["totalCount"]
    return "\n".join([
        f"📦 {repos:,} repositories  ·  {public:,} public  ·  **{private:,} private**",
        "",
        f"✍️ {year:,} commits in the last year  ·  {month:,} in the last 30 days",
        "",
        f"📈 {all_time:,} contributions since {since}",
        "",
        f"🔧 {' · '.join(languages)}",
    ])


def render_projects(config: dict, repos: list[dict]) -> str:
    """List every repo pushed to inside the window, most recent first.

    Nothing here is hand-curated. The one-line description is the repo's own
    GitHub description, so it is edited in one place — on the repo — and shows
    up here on the next run.
    """
    settings = config.get("projects", {})
    active_days = int(settings.get("active_days", 60))
    max_entries = int(settings.get("max_entries", 10))
    fallback_entries = int(settings.get("fallback_entries", 5))
    hidden = {str(n).lower() for n in (settings.get("hide") or [])}

    dated = []
    for repo in repos:
        if not repo.get("pushedAt") or repo["name"].lower() in hidden:
            continue
        when = datetime.strptime(repo["pushedAt"], "%Y-%m-%dT%H:%M:%SZ")
        dated.append((when.replace(tzinfo=timezone.utc), repo))
    dated.sort(key=lambda pair: pair[0], reverse=True)

    cutoff = datetime.now(timezone.utc) - timedelta(days=active_days)
    active = [pair for pair in dated if pair[0] >= cutoff][:max_entries]
    if active:
        chosen = active
        lead = f"Repositories I have pushed to in the last {active_days} days, most recent first."
    else:
        # A couple of quiet months should not empty the section.
        chosen = dated[:fallback_entries]
        lead = "Most recent work."

    if not chosen:
        fail("no repository to list — refusing to write an empty PROJECTS block")

    lines = [lead, ""]
    for when, repo in chosen:
        name = repo["name"]
        # Private repos cannot be linked, and saying so per line is the point of
        # the page rather than an apology for it.
        title = f"**{name}**" if repo["isPrivate"] else f"**[{name}]({repo['url']})**"
        bits = [title]
        description = (repo.get("description") or "").strip()
        if description:
            bits.append(f"— {description}")
        meta = []
        if repo.get("primaryLanguage"):
            meta.append(f"`{repo['primaryLanguage']['name']}`")
        meta.append("private" if repo["isPrivate"] else "public")
        meta.append(f"{when:%b %-d}")
        lines.append(f"{' '.join(bits)}  \n{' · '.join(meta)}")
        lines.append("")

    described = sum(1 for _, r in chosen if (r.get("description") or "").strip())
    if described < len(chosen):
        print(
            f"note: {len(chosen) - described} of {len(chosen)} listed repos have no "
            "GitHub description; they render as a bare name until you add one"
        )
    return "\n".join(lines).rstrip()


def replace_block(text: str, marker: str, body: str) -> str:
    pattern = re.compile(
        rf"(<!-- {marker}:START -->\n).*?(\n<!-- {marker}:END -->)",
        re.DOTALL,
    )
    if not pattern.search(text):
        fail(f"could not find the {marker} markers in README.md")
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text, count=1)


def main() -> None:
    token = os.environ.get("STATS_TOKEN", "").strip()
    if not token:
        fail("STATS_TOKEN is not set — the default GITHUB_TOKEN cannot see private repos")
    login = os.environ.get("GITHUB_LOGIN", "").strip()
    if not login:
        fail("GITHUB_LOGIN is not set")

    now = datetime.now(timezone.utc)
    # contributionsCollection accepts a window of at most one year.
    counts = graphql(token, COUNTS_QUERY, {
        "login": login,
        "from": iso(now - timedelta(days=365)),
        "to": iso(now),
    })
    window = graphql(token, WINDOW_QUERY, {
        "login": login,
        "from": iso(now - timedelta(days=30)),
        "to": iso(now),
    })

    commits_year = commits(counts["contributionsCollection"])
    commits_month = commits(window["contributionsCollection"])
    repos = fetch_repositories(token, login)
    languages = top_languages(repos)

    # Guards against writing a plausible-looking but wrong snapshot. A token
    # missing the repo scope reads as a real response with private repos at
    # zero, which is exactly the failure worth catching here.
    total = counts["all"]["totalCount"]
    scope_hint = "STATS_TOKEN needs the `repo` scope (classic) to see private repositories."
    if total == 0:
        fail(f"API reported 0 owned repositories — refusing to write. {scope_hint}")
    if counts["private"]["totalCount"] == 0:
        fail(
            "API reported 0 private repositories, which is the signature of a token "
            f"that cannot see them — refusing to write. {scope_hint}"
        )
    if len(repos) != total:
        fail(
            f"paginated {len(repos)} repositories but totalCount is {total} — "
            f"refusing to write on a partial read. {scope_hint}"
        )
    if counts["public"]["totalCount"] + counts["private"]["totalCount"] != total:
        fail("public + private does not equal the repository total — refusing to write")
    if commits_year == 0:
        fail(
            "API reported 0 commits in the last year — refusing to write. A classic "
            "token with `read:user` is required; fine-grained tokens often return 0 here."
        )
    if not languages:
        fail("no languages resolved across any repository — refusing to write")

    all_time, since = all_time_contributions(token, login, counts["createdAt"])
    if all_time == 0:
        fail("API reported 0 lifetime contributions — refusing to write")

    text = README.read_text(encoding="utf-8")
    updated = replace_block(
        text, "SNAPSHOT",
        render_snapshot(counts, commits_year, commits_month, languages, all_time, since),
    )
    updated = replace_block(
        updated, "PROJECTS",
        render_projects(yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}, repos),
    )

    if updated == text:
        print("README.md is already current; nothing to write.")
        return
    README.write_text(updated, encoding="utf-8")
    print(f"README.md updated — {total} repos, {commits_year} commits this year.")


if __name__ == "__main__":
    main()
