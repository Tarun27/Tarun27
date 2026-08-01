# Tarun Kumar

Senior software engineer, ~8 years in backend and distributed systems. Java and Spring professionally; Python, FastAPI and PostgreSQL for everything else.
Currently building retrieval systems over financial documents, and a lab for running distributed systems hard enough to watch them break.

### Stack

**Languages**
![Java](https://img.shields.io/badge/Java-1F6FEB?style=flat-square&logo=openjdk&logoColor=white)
![Python](https://img.shields.io/badge/Python-1F6FEB?style=flat-square&logo=python&logoColor=white)
![Kotlin](https://img.shields.io/badge/Kotlin-1F6FEB?style=flat-square&logo=kotlin&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-1F6FEB?style=flat-square&logo=typescript&logoColor=white)

**Backend & UI**
![Spring](https://img.shields.io/badge/Spring-246E9C?style=flat-square&logo=spring&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-246E9C?style=flat-square&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-246E9C?style=flat-square&logo=react&logoColor=white)
![Jetpack Compose](https://img.shields.io/badge/Jetpack%20Compose-246E9C?style=flat-square&logo=jetpackcompose&logoColor=white)

**Data**
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-2A6B7C?style=flat-square&logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-2A6B7C?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-2A6B7C?style=flat-square&logo=redis&logoColor=white)
![Cassandra](https://img.shields.io/badge/Cassandra-2A6B7C?style=flat-square&logo=apachecassandra&logoColor=white)

**Infra**
![Docker](https://img.shields.io/badge/Docker-30556B?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-30556B?style=flat-square&logo=githubactions&logoColor=white)
![Toxiproxy](https://img.shields.io/badge/Toxiproxy-30556B?style=flat-square&logo=proxy&logoColor=white)
![launchd](https://img.shields.io/badge/launchd-30556B?style=flat-square&logo=apple&logoColor=white)

### Snapshot

<!-- SNAPSHOT:START -->
📦 46 repositories  ·  21 public  ·  **25 private**

✍️ 581 commits in the last year  ·  151 in the last 30 days

🔧 Python · TypeScript · JavaScript · Java
<!-- SNAPSHOT:END -->

Most of what I build lives in private repositories, so the split is here to make the page reflect the actual volume of work rather than the public slice of it.

### Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-activity-graph.vercel.app/graph?username=Tarun27&days=31&area=true&hide_border=true&bg_color=0D1117&color=C9D1D9&title_color=58A6FF&line=58A6FF&point=58A6FF">
  <img alt="Contribution activity, last 31 days" src="https://github-readme-activity-graph.vercel.app/graph?username=Tarun27&days=31&area=true&hide_border=true&bg_color=FFFFFF&color=24292F&title_color=1F6FEB&line=1F6FEB&point=1F6FEB">
</picture>

The contribution calendar further down this profile page includes private work, so it reads closer to the truth than the repository list above it does.

### Projects

<!-- PROJECTS:START -->
Pushed to in the last 60 days.

**Local Apps Launcher** — Always-on daemon that starts and stops local apps on demand from a YAML registry.  
Health-check polling gates the browser redirect, so a request never lands on a port that is listening but not ready, and an idle reaper stops apps to reclaim RAM. Registered with launchd to survive reboots.  
`FastAPI` · `launchd` · `YAML` — _source private; happy to walk through the design or demo it_

**System Design Lab** — Learning distributed systems by running them, under synthetic traffic profiles and injected failure.  
Chaos injected through the Docker API and network conditions through Toxiproxy, with experiments defined in versioned YAML so a run is reproducible. Each one emits a labnote carrying measured p50/p95/p99 rather than a verdict.  
`Python` · `React` · `Docker` · `Cassandra` · `Redis` — _source private; happy to walk through the design or demo it_

**Doomscroll Vault** — Config-driven Instagram reel archiver built on Instaloader.  
An atomic manifest index with per-item metadata sidecars, so an interrupted run leaves the archive consistent and the next sync resumes incrementally instead of re-downloading. Sessions are reused to stay inside rate limits.  
`Python` · `Instaloader` — _source private; happy to walk through the design or demo it_

**ByteDesign** — System design concepts as an infinite vertical scroll feed, built for Android.  
Offline-first on Room with timestamp-based sync, cards rendered client-side in Compose so the payload stays text, and an on-device weighted-scoring recommender that orders the feed without a round trip.  
`Kotlin` · `Jetpack Compose` · `Room` — _source private; happy to walk through the design or demo it_
<!-- PROJECTS:END -->

### Contact

[tarunkr27@gmail.com](mailto:tarunkr27@gmail.com) · [LinkedIn](https://www.linkedin.com/in/REPLACE-ME)

Happy to walk through the design of any of the above, or screen-share the code.
