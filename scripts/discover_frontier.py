#!/usr/bin/env python3
"""Replayable breadth discovery for Track Tech Frontier research.

This intentionally small, standard-library-only CLI records metadata discovery
occurrences.  Its selected-repository GitHub observation command is a separate
post-screening enrichment path.  Neither path makes quality, adoption, growth,
or trend claims from a point-in-time repository star count.  Each command writes
JSONL records and a separate JSON run metadata document.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


DEFAULT_UA = "track-tech-frontier-discovery/1.0 (+https://platform.openai.com/codex)"
ARXIV_URL = "https://export.arxiv.org/api/query"
SEMANTIC_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
CROSSREF_URL = "https://api.crossref.org/works"
GITHUB_API = "https://api.github.com"


class DiscoveryError(RuntimeError):
    """An actionable discovery failure."""


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _date(value: str | None, option: str) -> str | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise DiscoveryError(f"{option} must be YYYY-MM-DD") from exc


def _nonnegative(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return number


def _positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least one")
    return number


def normalize_doi(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    result = value.strip().lower()
    result = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", result)
    result = re.sub(r"^doi:\s*", "", result)
    return result.rstrip(" .") or None


def normalize_arxiv(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    result = value.strip()
    result = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", result, flags=re.I)
    result = re.sub(r"^arXiv:", "", result, flags=re.I)
    result = re.sub(r"v\d+$", "", result, flags=re.I)
    return result.lower() or None


def normalized_title(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).split())


def first_author(authors: Any) -> str:
    if not isinstance(authors, list) or not authors:
        return ""
    item = authors[0]
    if isinstance(item, dict):
        item = item.get("name") or " ".join(
            str(item.get(part) or "").strip() for part in ("given", "family")
        ).strip()
    return normalized_title(item)


def paper_possible_duplicate_key(entity: dict[str, Any]) -> str | None:
    """Return a review hint, never an automatic cross-provider identity.

    Provider-native IDs are intentionally absent from this key.  It exists so
    the compiler can surface title/author/year collisions to a mapper while the
    occurrence ledger and provider-scoped entity identities remain intact.
    """
    title = normalized_title(entity.get("title"))
    if not title:
        return None
    raw_year = entity.get("year")
    if raw_year in (None, ""):
        published = entity.get("published_at")
        raw_year = str(published)[:4] if isinstance(published, str) else ""
    year = str(raw_year) if re.fullmatch(r"\d{4}", str(raw_year or "")) else ""
    return "possible-paper:" + "|".join((title, first_author(entity.get("authors")), year))


def paper_identity(entity: dict[str, Any], provider: str, raw_id: str) -> tuple[str, bool]:
    doi = normalize_doi(entity.get("doi"))
    if doi:
        return f"doi:{doi}", False
    arxiv = normalize_arxiv(entity.get("arxiv_id"))
    if arxiv:
        return f"arxiv:{arxiv}", False
    provider_id = str(entity.get("provider_id") or raw_id).strip()
    if provider_id:
        return f"provider:{provider}:{provider_id}", True
    fallback = paper_possible_duplicate_key(entity) or hashlib.sha256(
        json.dumps(entity, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    # A title-derived fallback is provider-scoped.  It must never merge two
    # providers automatically; the separate possible_duplicate_key is a review
    # hint only.
    return f"provider-fallback:{provider}:{fallback}", True


def repo_identity(entity: dict[str, Any], provider: str, raw_id: str) -> tuple[str, bool]:
    node_id = str(entity.get("node_id") or "").strip()
    return (f"github-node:{node_id}", False) if node_id else (f"provider:{provider}:{raw_id}", True)


def normalize_occurrence(record: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized copy and explicitly flag title-derived identities."""
    result = dict(record)
    entity = dict(result.get("entity") or {})
    kind = entity.get("kind")
    provider = str(result.get("provider") or "unknown")
    raw_id = str(result.get("raw_id") or entity.get("provider_id") or "")
    if kind == "paper":
        entity["doi"] = normalize_doi(entity.get("doi"))
        entity["arxiv_id"] = normalize_arxiv(entity.get("arxiv_id"))
        key, possible = paper_identity(entity, provider, raw_id)
        duplicate_hint = paper_possible_duplicate_key(entity) if possible else None
        if duplicate_hint:
            entity["possible_duplicate_key"] = duplicate_hint
        else:
            entity.pop("possible_duplicate_key", None)
    elif kind == "repository":
        key, possible = repo_identity(entity, provider, raw_id)
    else:
        key, possible = f"provider:{provider}:{raw_id}", True
    entity["dedupe_key"] = key
    entity["possible_duplicate"] = possible
    result["entity"] = entity
    return result


def _url(base: str, params: dict[str, Any]) -> str:
    pairs = [(key, str(value)) for key, value in params.items() if value is not None and value != ""]
    return f"{base}?{urlencode(pairs)}" if pairs else base


class Fetcher:
    def __init__(self, user_agent: str, retries: int, backoff: float, opener: Callable[..., Any] = urlopen):
        self.user_agent, self.retries, self.backoff, self.opener = user_agent, retries, backoff, opener

    def http(self, url: str) -> bytes:
        request = Request(url, headers={"User-Agent": self.user_agent, "Accept": "application/json, application/atom+xml;q=0.9"})
        for attempt in range(self.retries + 1):
            try:
                with self.opener(request, timeout=30) as response:
                    return response.read()
            except (HTTPError, URLError, TimeoutError) as exc:
                if attempt == self.retries:
                    raise DiscoveryError(f"HTTP request failed for {url}: {exc}") from exc
                time.sleep(self.backoff * (2 ** attempt))
        raise AssertionError("unreachable")

    def github(self, endpoint: str, params: dict[str, Any]) -> bytes:
        args = ["gh", "api", "--method", "GET", endpoint]
        for key, value in params.items():
            if value is not None:
                args.extend(("-f", f"{key}={value}"))
        for attempt in range(self.retries + 1):
            completed = subprocess.run(args, capture_output=True, check=False)
            if completed.returncode == 0:
                return completed.stdout
            if attempt == self.retries:
                detail = completed.stderr.decode("utf-8", "replace").strip()
                raise DiscoveryError(f"gh api failed for {endpoint}: {detail or 'unknown error'}")
            time.sleep(self.backoff * (2 ** attempt))
        raise AssertionError("unreachable")


def _save_raw(raw: bytes, raw_dir: Path | None, provider: str, ordinal: int) -> str | None:
    if raw_dir is None:
        return None
    raw_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(raw).hexdigest()
    path = raw_dir / f"{provider}-{ordinal:03d}-{digest}.raw"
    path.write_bytes(raw)
    return str(path)


def _paper(title: Any, authors: list[Any], provider_id: Any, url: Any, *, doi: Any = None, arxiv_id: Any = None,
           published_at: Any = None, revised_at: Any = None, year: Any = None, abstract: Any = None, venue: Any = None) -> dict[str, Any]:
    return {"kind": "paper", "title": str(title or ""), "authors": authors, "provider_id": str(provider_id or ""),
            "url": str(url or ""), "doi": doi, "arxiv_id": arxiv_id, "published_at": published_at,
            "revised_at": revised_at, "year": year, "abstract": abstract, "venue": venue}


def parse_arxiv(raw: bytes) -> tuple[list[dict[str, Any]], int | None]:
    root = ET.fromstring(raw)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    rows: list[dict[str, Any]] = []
    for entry in root.findall("a:entry", ns):
        ident = (entry.findtext("a:id", default="", namespaces=ns).rstrip("/").split("/")[-1])
        authors = [{"name": item.findtext("a:name", default="", namespaces=ns)} for item in entry.findall("a:author", ns)]
        rows.append(_paper(entry.findtext("a:title", default="", namespaces=ns), authors, ident,
                           entry.findtext("a:id", default="", namespaces=ns), arxiv_id=ident,
                           published_at=entry.findtext("a:published", default="", namespaces=ns),
                           revised_at=entry.findtext("a:updated", default="", namespaces=ns),
                           abstract=entry.findtext("a:summary", default="", namespaces=ns)))
    total = root.findtext("{http://a9.com/-/spec/opensearch/1.1/}totalResults")
    return rows, int(total) if total and total.isdigit() else None


def parse_semantic(raw: bytes) -> tuple[list[dict[str, Any]], int | None]:
    data = json.loads(raw.decode("utf-8"))
    rows = [_paper(item.get("title"), item.get("authors") or [], item.get("paperId"), item.get("url"),
                   doi=(item.get("externalIds") or {}).get("DOI"), arxiv_id=(item.get("externalIds") or {}).get("ArXiv"),
                   published_at=item.get("publicationDate"), year=item.get("year"), abstract=item.get("abstract"), venue=item.get("venue"))
            for item in data.get("data", [])]
    return rows, data.get("total") if isinstance(data.get("total"), int) else None


def parse_crossref(raw: bytes) -> tuple[list[dict[str, Any]], int | None]:
    message = json.loads(raw.decode("utf-8")).get("message", {})
    rows = []
    for item in message.get("items", []):
        parts = ((item.get("published-print") or item.get("published-online") or item.get("issued") or {}).get("date-parts") or [[None]])[0]
        published = "-".join(f"{int(value):02d}" if index else f"{int(value):04d}" for index, value in enumerate(parts) if value is not None) or None
        rows.append(_paper((item.get("title") or [""])[0], item.get("author") or [], item.get("DOI"), item.get("URL"),
                           doi=item.get("DOI"), published_at=published, year=parts[0] if parts else None,
                           abstract=item.get("abstract"), venue=(item.get("container-title") or [None])[0]))
    return rows, message.get("total-results") if isinstance(message.get("total-results"), int) else None


def parse_github(raw: bytes, commit_lookup: Callable[[str, str], str | None]) -> tuple[list[dict[str, Any]], int | None]:
    data = json.loads(raw.decode("utf-8"))
    rows: list[dict[str, Any]] = []
    for item in data.get("items", []):
        owner = (item.get("owner") or {}).get("login")
        name, branch = item.get("name"), item.get("default_branch")
        commit = commit_lookup(str(owner), str(branch)) if owner and name and branch else None
        rows.append({"kind": "repository", "title": item.get("full_name") or "", "provider_id": item.get("id"), "node_id": item.get("node_id"),
                     "url": item.get("html_url"), "owner": owner, "name": name, "owner_name": item.get("full_name"),
                     "created_at": item.get("created_at"), "pushed_at": item.get("pushed_at"), "stars": item.get("stargazers_count"),
                     "forks": item.get("forks_count"), "license": (item.get("license") or {}).get("spdx_id"), "default_branch": branch,
                     "default_branch_commit": commit, "default_branch_commit_status": "fetched" if commit else "unavailable",
                     "archived": item.get("archived"), "fork": item.get("fork"), "language": item.get("language"),
                     "description": item.get("description"), "topics": item.get("topics") or []})
    return rows, data.get("total_count") if isinstance(data.get("total_count"), int) else None


def provider_request(command: str, query: str, args: argparse.Namespace, page: int) -> tuple[str, dict[str, Any], Callable[[bytes], tuple[list[dict[str, Any]], int | None]]]:
    if command == "arxiv":
        # Scope the whole Boolean expression to all fields.  Without the
        # parentheses, `all:A OR B AND date` lets operator precedence leak B
        # outside the intended field/date scope and substantially raises noise.
        search_query = query if re.search(r"(?:^|\s|\()\w+:", query) else f"all:({query})"
        if args.from_date or args.to_date:
            start = (args.from_date or "0001-01-01").replace("-", "") + "0000"
            end = (args.to_date or "9999-12-31").replace("-", "") + "2359"
            search_query = f"{search_query} AND submittedDate:[{start} TO {end}]"
        params = {"search_query": search_query, "start": (page - 1) * args.limit, "max_results": args.limit,
                  "sortBy": "submittedDate", "sortOrder": "descending"}
        return ARXIV_URL, params, parse_arxiv
    if command == "semantic-scholar":
        year_range = None
        if args.from_date or args.to_date:
            year_range = f"{(args.from_date or '0001-01-01')[:4]}-{(args.to_date or '9999-12-31')[:4]}"
        params = {"query": query, "limit": args.limit, "offset": (page - 1) * args.limit, "year": year_range,
                  "fields": "paperId,title,authors,externalIds,publicationDate,year,abstract,url,venue"}
        return SEMANTIC_URL, params, parse_semantic
    if command == "crossref":
        filters = []
        if args.from_date: filters.append(f"from-pub-date:{args.from_date}")
        if args.to_date: filters.append(f"until-pub-date:{args.to_date}")
        params = {"query.bibliographic": query, "rows": args.limit, "offset": (page - 1) * args.limit,
                  "filter": ",".join(filters) or None, "select": "DOI,title,author,URL,published-print,published-online,issued,abstract,container-title"}
        return CROSSREF_URL, params, parse_crossref
    raise DiscoveryError(f"unsupported provider: {command}")


def _occurrences(provider: str, entities: Iterable[dict[str, Any]], request: dict[str, Any], observed_at: str, start_rank: int) -> list[dict[str, Any]]:
    result = []
    for offset, entity in enumerate(entities):
        raw_id = str(entity.get("provider_id") or entity.get("node_id") or "")
        result.append(normalize_occurrence({"record_type": "discovery-occurrence", "schema_version": "1.0", "provider": provider,
                                             "observed_at": observed_at, "rank": start_rank + offset, "raw_id": raw_id,
                                             "request": request, "entity": entity}))
    return result


def discover(command: str, args: argparse.Namespace, fetcher: Fetcher) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    _date(args.from_date, "--from"); _date(args.to_date, "--to")
    if args.from_date and args.to_date and args.from_date > args.to_date:
        raise DiscoveryError("--from must not be later than --to")
    outcomes, requests = [], []
    for index in range(args.pages):
        page = args.page + index
        if command == "github-search":
            qualifiers = [args.query]
            if args.from_date or args.to_date:
                qualifiers.append(f"{args.github_date_field}:{args.from_date or '*'}..{args.to_date or '*'}")
            params = {"q": " ".join(qualifiers), "per_page": args.limit, "page": page}
            endpoint = "/search/repositories"
            raw = fetcher.github(endpoint, params)
            data = json.loads(raw.decode("utf-8"))
            entities = []
            commit_requests = []
            for item_number, item in enumerate(data.get("items", []), 1):
                owner = (item.get("owner") or {}).get("login"); name = item.get("name"); branch = item.get("default_branch")
                commit = None
                # Broad discovery must stay broad: a search page is one API call,
                # while resolving every default-branch commit turns it into N+1.
                # Commit enrichment is therefore opt-in and belongs to mapping or
                # deep verification, after relevance screening has narrowed the set.
                if args.enrich_commits and owner and name and branch:
                    commit_endpoint = f"/repos/{owner}/{name}/commits/{branch}"
                    try:
                        commit_raw = fetcher.github(commit_endpoint, {})
                        detail = json.loads(commit_raw.decode("utf-8"))
                        commit = detail.get("sha")
                        commit_observed_at = utc_now()
                        commit_requests.append({"provider": command, "kind": "default-branch-commit", "url": GITHUB_API + commit_endpoint,
                                                "query": None, "params": {}, "page": page, "cursor": None, "observed_at": commit_observed_at,
                                                "result_count": 1, "reported_total": None, "response_sha256": hashlib.sha256(commit_raw).hexdigest(),
                                                "raw_snapshot_path": _save_raw(commit_raw, args.raw_dir, command, (index + 1) * 1000 + item_number)})
                    except DiscoveryError:
                        commit = None
                item["_default_branch_commit"] = commit
                entities.append(item)
            converted = []
            for item in entities:
                repo, _ = parse_github(json.dumps({"items": [item]}).encode("utf-8"), lambda _owner, _branch: item.get("_default_branch_commit"))
                converted.extend(repo)
            total = data.get("total_count") if isinstance(data.get("total_count"), int) else None
            exact_url = _url(GITHUB_API + endpoint, params)
        else:
            base, params, parser = provider_request(command, args.query, args, page)
            exact_url = _url(base, params)
            raw = fetcher.http(exact_url)
            converted, total = parser(raw)
        observed_at = utc_now(); snapshot = _save_raw(raw, args.raw_dir, command, index + 1)
        request = {"url": exact_url, "query": args.query, "params": params, "page": page, "cursor": args.cursor}
        outcomes.extend(_occurrences(command, converted, request, observed_at, (page - 1) * args.limit + 1))
        if command == "github-search":
            requests.extend(commit_requests)
        requests.append({"provider": command, "url": exact_url, "query": args.query, "params": params, "page": page,
                         "cursor": args.cursor, "observed_at": observed_at, "result_count": len(converted), "reported_total": total,
                         "response_sha256": hashlib.sha256(raw).hexdigest(), "raw_snapshot_path": snapshot})
        if index + 1 < args.pages and args.sleep:
            time.sleep(args.sleep)
    metadata = {"schema_version": "1.0", "record_type": "discovery-run", "provider": command, "query": args.query,
                "from": args.from_date, "to": args.to_date, "limit": args.limit, "pages": args.pages, "started_at": requests[0]["observed_at"] if requests else utc_now(),
                "finished_at": utc_now(), "requests": requests, "occurrence_count": len(outcomes),
                "github_date_field": args.github_date_field if command == "github-search" else None,
                "commit_enrichment": bool(command == "github-search" and args.enrich_commits),
                "limitations": "Metadata discovery only; stars are retained as discovery signals and are not quality, adoption, or trend evidence. Growth/acceleration requires two dated observations."}
    return outcomes, metadata


def _github_date(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) < 10:
        raise DiscoveryError(f"GitHub repository {field} is unavailable")
    try:
        return date.fromisoformat(value[:10]).isoformat()
    except ValueError as exc:
        raise DiscoveryError(f"GitHub repository {field} is malformed") from exc


def observe_github(args: argparse.Namespace, fetcher: Fetcher) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Collect a replayable, complete observation for one selected repository."""
    from_date = _date(args.from_date, "--from")
    to_date = _date(args.to_date, "--to")
    if from_date is None or to_date is None:
        raise DiscoveryError("github-observe requires both --from and --to")
    if from_date > to_date:
        raise DiscoveryError("--from must not be later than --to")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        raise DiscoveryError("--repo must be OWNER/REPO")

    requests: list[dict[str, Any]] = []
    ordinal = 0

    def fetch_json(kind: str, endpoint: str, params: dict[str, Any]) -> Any:
        nonlocal ordinal
        ordinal += 1
        raw = fetcher.github(endpoint, params)
        retrieved_at = utc_now()
        snapshot = _save_raw(raw, args.raw_dir, "github-observe", ordinal)
        if snapshot is None:
            raise DiscoveryError("github-observe requires replayable raw snapshots")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DiscoveryError(f"GitHub {kind} response is not valid UTF-8 JSON") from exc
        result_count = len(value) if isinstance(value, list) else 1
        requests.append({"provider": "github-observe", "kind": kind, "url": _url(GITHUB_API + endpoint, params),
                         "params": params, "retrieved_at": retrieved_at, "observed_at": retrieved_at,
                         "result_count": result_count, "response_sha256": hashlib.sha256(raw).hexdigest(),
                         "raw_snapshot_path": snapshot})
        return value

    requested_endpoint = f"/repos/{args.repo}"
    repository = fetch_json("repository", requested_endpoint, {})
    if not isinstance(repository, dict):
        raise DiscoveryError("GitHub repository response must be an object")
    full_name, node_id, default_branch = repository.get("full_name"), repository.get("node_id"), repository.get("default_branch")
    provider_id = repository.get("id")
    if not all(isinstance(value, str) and value for value in (full_name, node_id, default_branch)) or provider_id in (None, ""):
        raise DiscoveryError("GitHub repository identity/default branch is incomplete")
    canonical_endpoint = f"/repos/{full_name}"

    releases = fetch_json("latest-release", canonical_endpoint + "/releases", {"per_page": 1, "page": 1})
    if not isinstance(releases, list):
        raise DiscoveryError("GitHub releases response must be an array")
    latest_release = None
    if releases:
        if not isinstance(releases[0], dict):
            raise DiscoveryError("GitHub latest release record is malformed")
        release_date = releases[0].get("published_at") or releases[0].get("created_at")
        latest_release = _github_date(release_date, "latest release date")

    encoded_branch = quote(default_branch, safe="")
    default_commit_record = fetch_json("default-branch-commit", canonical_endpoint + f"/commits/{encoded_branch}", {})
    default_commit = default_commit_record.get("sha") if isinstance(default_commit_record, dict) else None
    if not isinstance(default_commit, str) or not default_commit:
        raise DiscoveryError("GitHub default-branch commit SHA is unavailable")

    commit_shas: set[str] = set()
    contributor_keys: set[str] = set()
    page = 1
    while True:
        params = {"sha": default_branch, "since": from_date + "T00:00:00Z", "until": to_date + "T23:59:59Z",
                  "per_page": 100, "page": page}
        commits = fetch_json("commits-in-window", canonical_endpoint + "/commits", params)
        if not isinstance(commits, list):
            raise DiscoveryError("GitHub commit-window response must be an array")
        for commit in commits:
            if not isinstance(commit, dict) or not isinstance(commit.get("sha"), str) or not commit["sha"]:
                raise DiscoveryError("GitHub commit-window response contains a commit without a SHA")
            if commit["sha"] in commit_shas:
                raise DiscoveryError("GitHub commit pagination returned a duplicate SHA; measurement is not complete")
            commit_shas.add(commit["sha"])
            login = (commit.get("author") or {}).get("login") if isinstance(commit.get("author"), dict) else None
            git_author = (commit.get("commit") or {}).get("author") if isinstance(commit.get("commit"), dict) else None
            fallback = None
            if isinstance(git_author, dict):
                fallback = git_author.get("email") or git_author.get("name")
            contributor = f"login:{login}" if isinstance(login, str) and login else (
                f"git-author:{str(fallback).strip().casefold()}" if fallback else None
            )
            if contributor is None:
                raise DiscoveryError("GitHub commit lacks an attributable author; contributors_in_window is unknown")
            contributor_keys.add(contributor)
        if len(commits) < 100:
            break
        page += 1
        if args.sleep:
            time.sleep(args.sleep)

    counters = {"stars": repository.get("stargazers_count"), "forks": repository.get("forks_count"),
                "open_issues": repository.get("open_issues_count")}
    if any(type(value) is not int or value < 0 for value in counters.values()):
        raise DiscoveryError("GitHub repository counters are unavailable; refusing to encode unknown as zero")
    if not isinstance(repository.get("archived"), bool) or not isinstance(repository.get("fork"), bool):
        raise DiscoveryError("GitHub repository archived/fork state is unavailable")
    observed_at = utc_now()
    observation = {
        "provider_result_id": str(provider_id), "node_id": node_id, "owner_repo": full_name,
        **counters, "created": _github_date(repository.get("created_at"), "created_at"),
        "pushed": _github_date(repository.get("pushed_at"), "pushed_at"),
        "latest_release": latest_release, "default_commit": default_commit,
        "archived": repository["archived"], "fork": repository["fork"],
        "license": (repository.get("license") or {}).get("spdx_id") if isinstance(repository.get("license"), dict) else None,
        "commits_in_window": len(commit_shas), "contributors_in_window": len(contributor_keys),
        "window_id": args.window_id, "api_url": GITHUB_API + canonical_endpoint,
        "note": "GitHub REST snapshot; commit and unique-contributor counts cover the requested inclusive UTC window. Stars are cumulative and are not growth evidence.",
        "observed_at": observed_at,
        "measurement_basis": {"entity_freshness": "created", "recent_activity": "pushed",
                              "commit_window": {"from": from_date, "to": to_date},
                              "request_raw_snapshots": [item["raw_snapshot_path"] for item in requests]},
    }
    metadata = {"schema_version": "1.0", "record_type": "github-repository-observation-run",
                "provider": "github-observe", "repo_requested": args.repo, "repo_observed": full_name,
                "from": from_date, "to": to_date, "window_id": args.window_id,
                "started_at": requests[0]["retrieved_at"], "finished_at": observed_at,
                "requests": requests, "observation_count": 1, "measurement_status": "complete",
                "limitations": "Point-in-time stars are retained only as a snapshot. No growth or acceleration is inferred."}
    return [observation], metadata


def _read_jsonl(paths: list[Path]) -> list[dict[str, Any]]:
    values = []
    for path in paths:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip(): continue
            try: value = json.loads(line)
            except json.JSONDecodeError as exc: raise DiscoveryError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(value, dict): raise DiscoveryError(f"{path}:{line_number}: expected JSON object")
            values.append(value)
    return values


def local_transform(command: str, args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    input_records = _read_jsonl(args.input)
    records = [normalize_occurrence(item) for item in input_records]
    removed = 0
    if command == "merge":
        # Merge is an occurrence-ledger operation, not an entity-deduplication
        # view.  Preserve provider/query/rank/request occurrences even when they
        # describe the same DOI, arXiv paper, or GitHub node.  Only an identical
        # normalized occurrence object is redundant.
        selected: dict[str, dict[str, Any]] = {}
        for item in records:
            key = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            selected.setdefault(key, item)
        records = list(selected.values())
        removed = len(input_records) - len(records)
    return records, {"schema_version": "1.0", "record_type": "discovery-run", "provider": command, "query": None,
                     "from": None, "to": None, "limit": None, "pages": None, "started_at": utc_now(), "finished_at": utc_now(),
                     "inputs": [str(path) for path in args.input], "input_count": len(input_records), "occurrence_count": len(records),
                     "exact_duplicate_occurrences_removed": removed,
                     "limitations": "Merge preserves the occurrence ledger and removes only identical normalized occurrence objects. Entity deduplication is a separate compiler view; title/author/year collisions remain mapper-reviewed possible duplicates."}


def _write_jsonl(records: Iterable[dict[str, Any]], path: Path | None) -> None:
    stream = sys.stdout if path is None else path.open("w", encoding="utf-8", newline="\n")
    try:
        for item in records:
            stream.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")
    finally:
        if path is not None: stream.close()


def _write_metadata(metadata: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("arxiv", "semantic-scholar", "crossref", "github-search"):
        sub = commands.add_parser(name, help=f"discover from {name}")
        sub.add_argument("--query", required=True); sub.add_argument("--from", dest="from_date"); sub.add_argument("--to", dest="to_date")
        sub.add_argument("--limit", type=_positive, default=25); sub.add_argument("--page", type=_positive, default=1); sub.add_argument("--pages", type=_positive, default=1)
        sub.add_argument("--cursor", help="opaque provider cursor recorded for replay; supported providers use page/offset pagination")
        sub.add_argument("--sleep", type=float, default=0.0); sub.add_argument("--backoff", type=float, default=1.0); sub.add_argument("--retries", type=_nonnegative, default=2)
        sub.add_argument("--user-agent", default=DEFAULT_UA); sub.add_argument("--raw-dir", type=Path)
        sub.add_argument("--enrich-commits", action="store_true",
                         help="GitHub only: fetch each result's default-branch commit; use after broad screening")
        if name == "github-search":
            sub.add_argument("--github-date-field", choices=("created", "pushed"), default="created",
                             help="GitHub qualifier for --from/--to (creation or activity recency)")
        sub.add_argument("--output", type=Path); sub.add_argument("--metadata", required=True, type=Path)
    for name in ("normalize", "merge"):
        help_text = ("normalize JSONL discovery occurrences" if name == "normalize" else
                     "combine occurrence ledgers; remove only identical normalized occurrences")
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument("--input", required=True, type=Path, action="append"); sub.add_argument("--output", required=True, type=Path); sub.add_argument("--metadata", required=True, type=Path)
    observe = commands.add_parser("github-observe", help="collect a replayable complete observation for one selected GitHub repository")
    observe.add_argument("--repo", required=True, help="selected repository as OWNER/REPO")
    observe.add_argument("--from", dest="from_date", required=True); observe.add_argument("--to", dest="to_date", required=True)
    observe.add_argument("--window-id", required=True, help="bundle time-window ID represented by the commit count")
    observe.add_argument("--sleep", type=float, default=0.0); observe.add_argument("--backoff", type=float, default=1.0)
    observe.add_argument("--retries", type=_nonnegative, default=2); observe.add_argument("--user-agent", default=DEFAULT_UA)
    observe.add_argument("--raw-dir", required=True, type=Path); observe.add_argument("--output", required=True, type=Path)
    observe.add_argument("--metadata", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command in {"normalize", "merge"}: records, metadata = local_transform(args.command, args)
        elif args.command == "github-observe": records, metadata = observe_github(args, Fetcher(args.user_agent, args.retries, args.backoff))
        else: records, metadata = discover(args.command, args, Fetcher(args.user_agent, args.retries, args.backoff))
        _write_jsonl(records, getattr(args, "output", None)); _write_metadata(metadata, args.metadata)
        return 0
    except (DiscoveryError, OSError, ValueError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 2


if __name__ == "__main__":
    raise SystemExit(main())
