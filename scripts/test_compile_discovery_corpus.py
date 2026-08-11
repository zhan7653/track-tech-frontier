from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import compile_discovery_corpus as target


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


class CompilerTests(unittest.TestCase):
    def make_bundle(self, root: Path) -> Path:
        bundle = root / "bundle"; bundle.mkdir()
        write_json(bundle / "research_plan.json", {"as_of":"2026-08-10", "lanes": ["paper", "github"], "time_windows": ["W1"]})
        write_jsonl(bundle / "time_windows.jsonl", [{"window_id": "W1", "label": "test", "start": "2024-01-01", "end": "2024-12-31", "kind": "custom"}])
        for name in ("clusters.jsonl", "gaps.jsonl", "queries.jsonl", "discovery_results.jsonl", "entities.jsonl", "repository_observations.jsonl"):
            (bundle / name).write_text("", encoding="utf-8")
        return bundle

    def run_compile(self, root: Path, queries: list[dict]) -> tuple[Path, dict]:
        bundle = self.make_bundle(root); spec = root / "spec.json"; summary = root / "summary.json"
        write_json(spec, {"queries": queries})
        result = target.compile_spec(bundle, spec, summary)
        return bundle, result

    def test_merges_doi_entities_and_assigns_every_occurrence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "papers.jsonl"; run = root / "run.json"
            write_jsonl(occurrences, [
                {"provider":"crossref", "raw_id":"a", "observed_at":"2026-01-02T00:00:00Z", "rank":1, "request":{"url":"https://api.example/a","page":1,"cursor":None}, "entity":{"kind":"paper","title":"First title","url":"https://doi.org/10/a","dedupe_key":"doi:10/a","published_at":"2024-01-01"}},
                {"provider":"semantic-scholar", "raw_id":"b", "observed_at":"2026-01-02T00:00:01Z", "rank":2, "request":{"url":"https://api.example/b","page":1,"cursor":None}, "entity":{"kind":"paper","title":"Alias title","url":"https://doi.org/10/a","dedupe_key":"doi:10/a","published_at":"2024"}},
            ])
            write_json(run, {"provider":"crossref", "query":"topic", "started_at":"2026-01-02T00:00:00Z", "requests":[{"url":"https://api.example/a", "raw_snapshot_path":"raw/a"}]})
            bundle, summary = self.run_compile(root, [{"query_id":"Q1", "occurrence_jsonl":"papers.jsonl", "run_metadata":"run.json", "stage":"discover", "lanes":["paper"], "windows":["W1"], "parents":[], "gaps":[], "information_gain":"Two independent indexes."}])
            entities = target.read_jsonl(bundle / "entities.jsonl", "entities")
            discoveries = target.read_jsonl(bundle / "discovery_results.jsonl", "discoveries")
            self.assertEqual(len(entities), 1); self.assertEqual(len(entities[0]["discovery_ids"]), 2)
            self.assertEqual(set(entities[0]["discovery_ids"]), {row["discovery_id"] for row in discoveries})
            self.assertEqual(summary["occurrences_imported"], 2)

    def test_unmeasured_github_is_skipped_not_zeroed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "repos.jsonl"; run = root / "run.json"
            write_jsonl(occurrences, [{"provider":"github-search", "raw_id":"1", "observed_at":"2026-01-02T00:00:00Z", "rank":1, "request":{"url":"https://api.github.com/search/repositories","page":1,"cursor":None}, "entity":{"kind":"repository","title":"o/r","url":"https://github.com/o/r","dedupe_key":"github-node:R1","node_id":"R1", "owner_name":"o/r"}}])
            write_json(run, {"provider":"github-search", "query":"topic", "started_at":"2026-01-02T00:00:00Z", "requests":[]})
            bundle, summary = self.run_compile(root, [{"query_id":"QG", "occurrence_jsonl":"repos.jsonl", "run_metadata":"run.json", "stage":"discover", "lanes":["github"], "windows":["W1"], "parents":[], "gaps":[], "information_gain":"Repository recall."}])
            self.assertEqual(target.read_jsonl(bundle / "repository_observations.jsonl", "observations"), [])
            self.assertEqual(summary["repository_observations_skipped_unmeasured_count"], 1)

    def test_exact_year_and_unknown_dates_use_intervals_without_query_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "papers.jsonl"; run = root / "run.json"
            write_jsonl(occurrences, [
                {"provider":"crossref", "raw_id":"exact", "observed_at":"2026-01-02T00:00:00Z", "rank":1, "request":{}, "entity":{"kind":"paper","title":"Exact","url":"https://doi.org/10/exact","dedupe_key":"doi:10/exact","published_at":"2024-06-20"}},
                {"provider":"crossref", "raw_id":"year", "observed_at":"2026-01-02T00:00:01Z", "rank":2, "request":{}, "entity":{"kind":"paper","title":"Year","url":"https://doi.org/10/year","dedupe_key":"doi:10/year","published_at":"2025"}},
                {"provider":"crossref", "raw_id":"unknown", "observed_at":"2026-01-02T00:00:02Z", "rank":3, "request":{}, "entity":{"kind":"paper","title":"Unknown","url":"https://doi.org/10/unknown","dedupe_key":"doi:10/unknown"}},
            ])
            write_json(run, {"provider":"crossref", "query":"topic", "started_at":"2026-01-02T00:00:00Z", "requests":[]})
            bundle = self.make_bundle(root)
            write_jsonl(bundle / "time_windows.jsonl", [
                {"window_id":"W2024", "label":"2024", "start":"2024-01-01", "end":"2024-12-31", "kind":"custom"},
                {"window_id":"W2025", "label":"2025", "start":"2025-01-01", "end":"2025-12-31", "kind":"custom"},
                {"window_id":"WTarget", "label":"target", "start":"2026-01-01", "end":"2026-12-31", "kind":"custom"},
            ])
            spec = root / "spec.json"; summary_path = root / "summary.json"
            write_json(spec, {"queries":[{"query_id":"Q1", "occurrence_jsonl":"papers.jsonl", "run_metadata":"run.json", "stage":"discover", "lanes":["paper"], "windows":["WTarget"], "parents":[], "gaps":[], "information_gain":"Date semantics."}]})
            summary = target.compile_spec(bundle, spec, summary_path)
            by_key = {row["identifier"]: row for row in target.read_jsonl(bundle / "entities.jsonl", "entities")}
            self.assertEqual(by_key["doi:10/exact"]["time_window_ids"], ["W2024"])
            self.assertEqual(by_key["doi:10/year"]["time_window_ids"], ["W2025"])
            self.assertIsNone(by_key["doi:10/year"]["published_at"])
            self.assertEqual(by_key["doi:10/unknown"]["time_window_ids"], [])
            self.assertEqual(summary["entity_time_windows_unknown_date_count"], 1)
            self.assertEqual(summary["entity_time_windows_unknown_date"][0]["reason"], "entity_date_unknown_query_target_windows_not_inherited")

    def test_recent_windows_require_coarse_dates_to_fit_wholly_and_not_pass_as_of(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "papers.jsonl"; run = root / "run.json"
            rows = []
            for rank, (raw_id, published) in enumerate((("exact","2026-05-13"), ("partial-year","2025"), ("partial-month","2026-05"), ("future-tail-month","2026-08"), ("unknown",None)), 1):
                entity = {"kind":"paper","title":raw_id,"url":f"https://example.test/{raw_id}","dedupe_key":f"provider:test:{raw_id}"}
                if raw_id == "partial-year": entity["year"] = int(published)
                elif published is not None: entity["published_at"] = published
                rows.append({"provider":"test","raw_id":raw_id,"observed_at":"2026-08-10T00:00:00Z","rank":rank,"request":{},"entity":entity})
            write_jsonl(occurrences, rows)
            write_json(run, {"provider":"test","query":"topic","started_at":"2026-08-10T00:00:00Z","requests":[]})
            bundle = self.make_bundle(root)
            write_jsonl(bundle / "time_windows.jsonl", [
                {"window_id":"WEST","label":"established","start":"2025-01-01","end":"2026-08-10","kind":"established"},
                {"window_id":"W12","label":"rolling 12m","start":"2025-08-11","end":"2026-08-10","kind":"recent-12m"},
                {"window_id":"W90","label":"rolling 90d","start":"2026-05-13","end":"2026-08-10","kind":"recent-90d"},
            ])
            spec = root / "spec.json"; summary_path = root / "summary.json"
            write_json(spec, {"queries":[{"query_id":"Q1","occurrence_jsonl":"papers.jsonl","run_metadata":"run.json","stage":"discover","lanes":["paper"],"windows":["W90"],"parents":[],"gaps":[],"information_gain":"Conservative recent-date semantics."}]})
            summary = target.compile_spec(bundle, spec, summary_path)
            by_name = {row["canonical_name"]:row for row in target.read_jsonl(bundle / "entities.jsonl", "entities")}
            self.assertEqual(by_name["exact"]["time_window_ids"], ["WEST", "W12", "W90"])
            self.assertEqual(by_name["partial-year"]["time_window_ids"], ["WEST"])
            self.assertEqual(by_name["partial-month"]["time_window_ids"], ["WEST", "W12"])
            self.assertEqual(by_name["future-tail-month"]["time_window_ids"], ["WEST"])
            self.assertEqual(by_name["unknown"]["time_window_ids"], [])
            self.assertEqual(summary["entity_time_windows_unknown_date_count"], 1)

    def test_complete_explicit_github_observation_is_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "repos.jsonl"; run = root / "run.json"
            write_jsonl(occurrences, [{"provider":"github-search", "raw_id":"1", "observed_at":"2026-01-02T00:00:00Z", "rank":1, "request":{"url":"https://api.github.com/search/repositories","page":1,"cursor":None}, "entity":{"kind":"repository","title":"o/r","url":"https://github.com/o/r","dedupe_key":"github-node:R1","node_id":"R1", "created_at":"2024-06-01T00:00:00Z"}}])
            write_json(run, {"provider":"github-search", "query":"topic", "started_at":"2026-01-02T00:00:00Z", "requests":[]})
            observation = {"provider_result_id":"1", "node_id":"R1", "owner_repo":"o/r", "stars":3, "forks":1, "open_issues":2, "created":"2024-01-01", "pushed":"2026-01-01", "latest_release":None, "default_commit":"abcdef0", "archived":False, "fork":False, "license":"MIT", "commits_in_window":4, "contributors_in_window":2, "window_id":"W1", "api_url":"https://api.github.com/repos/o/r", "note":"GitHub REST API counters, metadata only.", "observed_at":"2026-01-02T00:00:00Z"}
            bundle, summary = self.run_compile(root, [{"query_id":"QG", "occurrence_jsonl":"repos.jsonl", "run_metadata":"run.json", "stage":"discover", "lanes":["github"], "windows":["W1"], "parents":[], "gaps":[], "information_gain":"Repository recall.", "repository_observations":[observation]}])
            rows = target.read_jsonl(bundle / "repository_observations.jsonl", "observations")
            self.assertEqual(len(rows), 1); self.assertEqual(rows[0]["open_issues"], 2)
            repo_entity = target.read_jsonl(bundle / "entities.jsonl", "entities")[0]
            self.assertEqual(repo_entity["time_window_ids"], ["W1"])
            self.assertIsNone(repo_entity["published_at"])
            self.assertEqual(summary["repository_observations_skipped_unmeasured_count"], 0)

    def test_old_created_recent_pushed_repository_separates_creation_and_activity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "repos.jsonl"; run = root / "run.json"
            write_jsonl(occurrences, [{"provider":"github-search","raw_id":"1","observed_at":"2026-08-10T00:00:00Z","rank":1,"request":{},"entity":{"kind":"repository","title":"o/old-active","url":"https://github.com/o/old-active","dedupe_key":"github-node:R-old","node_id":"R-old","created_at":"2020-01-02T00:00:00Z","pushed_at":"2026-07-15T00:00:00Z"}}])
            write_json(run, {"provider":"github-search","query":"topic pushed:2026-05-13..2026-08-10","started_at":"2026-08-10T00:00:00Z","requests":[]})
            bundle = self.make_bundle(root)
            write_jsonl(bundle / "time_windows.jsonl", [
                {"window_id":"WOLD","label":"established","start":"2019-01-01","end":"2025-08-10","kind":"established"},
                {"window_id":"W90","label":"recent activity","start":"2026-05-13","end":"2026-08-10","kind":"recent-90d"},
            ])
            spec = root / "spec.json"; summary_path = root / "summary.json"
            write_json(spec, {"queries":[{"query_id":"QG","occurrence_jsonl":"repos.jsonl","run_metadata":"run.json","stage":"discover","lanes":["github"],"windows":["W90"],"parents":[],"gaps":[],"information_gain":"Recent repository activity recall."}]})
            summary = target.compile_spec(bundle, spec, summary_path)
            entity = target.read_jsonl(bundle / "entities.jsonl", "entities")[0]
            self.assertEqual(entity["time_window_ids"], ["WOLD"])
            basis = summary["repository_freshness_basis"][0]
            self.assertEqual(basis["entity_freshness_basis"], "repository_created_at")
            self.assertEqual(basis["creation_time_window_ids"], ["WOLD"])
            self.assertEqual(basis["activity_basis"], "repository_pushed_at")
            self.assertEqual(basis["recent_activity_window_ids"], ["W90"])
            self.assertEqual(summary["repository_creation_counts_by_window"], {"W90":0,"WOLD":1})
            self.assertEqual(summary["repository_activity_counts_by_window"], {"W90":1,"WOLD":0})
            self.assertEqual(summary["repository_recent_activity_counts_by_window"], {"W90":1})
            self.assertEqual(summary["repositories_with_recent_activity_count"], 1)

    def test_cross_provider_no_strong_id_creates_review_group_without_merging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "papers.jsonl"; run = root / "run.json"
            write_jsonl(occurrences, [
                {"provider":"crossref","raw_id":"CR1","observed_at":"2026-08-10T00:00:00Z","rank":1,"request":{},"entity":{"kind":"paper","title":"The Same Paper","authors":[{"given":"Ada","family":"Lovelace"}],"year":2024,"published_at":"2024","url":"https://example.test/cr1","dedupe_key":"provider:crossref:CR1","possible_duplicate":True}},
                {"provider":"semantic-scholar","raw_id":"SS1","observed_at":"2026-08-10T00:00:01Z","rank":2,"request":{},"entity":{"kind":"paper","title":"the same paper!","authors":[{"name":"Ada Lovelace"}],"url":"https://example.test/ss1","dedupe_key":"provider:semantic-scholar:SS1","possible_duplicate":True}},
            ])
            write_json(run, {"provider":"mixed","query":"topic","started_at":"2026-08-10T00:00:00Z","requests":[]})
            bundle, summary = self.run_compile(root, [{"query_id":"QP","occurrence_jsonl":"papers.jsonl","run_metadata":"run.json","stage":"discover","lanes":["paper"],"windows":["W1"],"parents":[],"gaps":[],"information_gain":"Cross-provider recall."}])
            self.assertEqual(len(target.read_jsonl(bundle / "entities.jsonl", "entities")), 2)
            self.assertEqual(summary["possible_duplicate_group_count"], 1)
            group = summary["possible_duplicate_groups"][0]
            self.assertEqual(set(group["providers"]), {"crossref", "semantic-scholar"})
            self.assertEqual(len(group["entity_ids"]), 2)
            self.assertEqual(group["year"], "2024")
            self.assertTrue(group["requires_mapper_review"])

    def test_incomplete_explicit_observation_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); occurrences = root / "repos.jsonl"; run = root / "run.json"
            write_jsonl(occurrences, [{"provider":"github-search", "raw_id":"1", "observed_at":"2026-01-02T00:00:00Z", "rank":1, "request":{}, "entity":{"kind":"repository","title":"o/r","url":"https://github.com/o/r","dedupe_key":"github-node:R1"}}])
            write_json(run, {"provider":"github-search", "query":"topic", "started_at":"2026-01-02T00:00:00Z"})
            bundle = self.make_bundle(root); spec = root / "spec.json"; summary = root / "summary.json"
            write_json(spec, {"queries":[{"query_id":"QG", "occurrence_jsonl":"repos.jsonl", "run_metadata":"run.json", "stage":"discover", "lanes":["github"], "windows":["W1"], "parents":[], "gaps":[], "information_gain":"Repository recall.", "repository_observations":[{"provider_result_id":"1"}]}]})
            with self.assertRaisesRegex(target.CompileError, "incomplete API-derived"):
                target.compile_spec(bundle, spec, summary)
            self.assertEqual((bundle / "queries.jsonl").read_text(encoding="utf-8"), "")


if __name__ == "__main__":
    unittest.main()
