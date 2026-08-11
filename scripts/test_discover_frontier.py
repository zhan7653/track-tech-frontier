from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import discover_frontier as target


class IdentityTests(unittest.TestCase):
    def test_doi_precedes_arxiv_and_title_fallback_is_possible(self):
        record = target.normalize_occurrence({"provider": "crossref", "raw_id": "x", "entity": {"kind": "paper", "doi": "https://doi.org/10.1/ABC.", "arxiv_id": "2401.12345v2", "title": "Ignored"}})
        self.assertEqual(record["entity"]["dedupe_key"], "doi:10.1/abc")
        record = target.normalize_occurrence({"provider": "arxiv", "raw_id": "", "entity": {"kind": "paper", "title": " A: Test ", "authors": [{"name": "Ada Lovelace"}], "year": 2024}})
        self.assertTrue(record["entity"]["possible_duplicate"])
        self.assertEqual(record["entity"]["dedupe_key"], "provider-fallback:arxiv:possible-paper:a test|ada lovelace|2024")
        self.assertEqual(record["entity"]["possible_duplicate_key"], "possible-paper:a test|ada lovelace|2024")

    def test_provider_ids_stay_distinct_but_share_possible_duplicate_hint(self):
        crossref = target.normalize_occurrence({"provider":"crossref", "raw_id":"CR-1", "entity":{"kind":"paper", "provider_id":"CR-1", "title":"Same Paper!", "authors":[{"given":"Ada", "family":"Lovelace"}], "year":2025}})
        semantic = target.normalize_occurrence({"provider":"semantic-scholar", "raw_id":"SS-1", "entity":{"kind":"paper", "provider_id":"SS-1", "title":"same paper", "authors":[{"name":"Ada Lovelace"}], "published_at":"2025-03-01"}})
        self.assertNotEqual(crossref["entity"]["dedupe_key"], semantic["entity"]["dedupe_key"])
        self.assertEqual(crossref["entity"]["possible_duplicate_key"], semantic["entity"]["possible_duplicate_key"])

    def test_github_uses_node_id(self):
        record = target.normalize_occurrence({"provider": "github-search", "raw_id": "99", "entity": {"kind": "repository", "node_id": "R_kgDOA"}})
        self.assertEqual(record["entity"]["dedupe_key"], "github-node:R_kgDOA")


class ParsingTests(unittest.TestCase):
    def test_arxiv_boolean_query_is_parenthesized_before_date_filter(self):
        parser = target.build_parser()
        args = parser.parse_args(["arxiv", "--query", '"agent memory" OR "long-term memory"', "--from", "2025-01-01", "--to", "2026-08-10", "--metadata", "unused.json"])
        _, params, _ = target.provider_request("arxiv", args.query, args, 1)
        self.assertEqual(params["search_query"], 'all:("agent memory" OR "long-term memory") AND submittedDate:[202501010000 TO 202608102359]')

    def test_crossref_fixture(self):
        raw = b'{"message":{"total-results":1,"items":[{"DOI":"10.2/X","title":["Paper"],"author":[{"given":"Ada","family":"Lovelace"}],"URL":"https://doi.org/10.2/X","issued":{"date-parts":[[2024,2,3]]}}]}}'
        rows, total = target.parse_crossref(raw)
        self.assertEqual(total, 1); self.assertEqual(rows[0]["doi"], "10.2/X"); self.assertEqual(rows[0]["published_at"], "2024-02-03")

    def test_arxiv_fixture(self):
        raw = b'''<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"><opensearch:totalResults>1</opensearch:totalResults><entry><id>http://arxiv.org/abs/2401.00001v3</id><title> Test </title><author><name>Ada</name></author><published>2024-01-01T00:00:00Z</published><updated>2024-01-02T00:00:00Z</updated><summary>Abstract</summary></entry></feed>'''
        rows, total = target.parse_arxiv(raw)
        self.assertEqual(total, 1); self.assertEqual(rows[0]["arxiv_id"], "2401.00001v3")

    def test_github_fixture_collects_commit(self):
        raw = b'{"total_count":1,"items":[{"id":1,"node_id":"R1","full_name":"octo/demo","name":"demo","owner":{"login":"octo"},"html_url":"https://github.com/octo/demo","default_branch":"main","stargazers_count":5,"forks_count":2,"license":{"spdx_id":"MIT"}}]}'
        rows, total = target.parse_github(raw, lambda owner, branch: "abc123")
        self.assertEqual(total, 1); self.assertEqual(rows[0]["default_branch_commit"], "abc123")
        self.assertEqual(rows[0]["owner_name"], "octo/demo")


class CliTests(unittest.TestCase):
    def test_github_discovery_does_not_enrich_commits_by_default(self):
        class FakeFetcher:
            def __init__(self):
                self.calls = []

            def github(self, endpoint, params):
                self.calls.append((endpoint, params))
                if endpoint != "/search/repositories":
                    raise AssertionError("broad discovery must not make per-repository calls")
                return b'{"total_count":1,"items":[{"id":1,"node_id":"R1","full_name":"octo/demo","name":"demo","owner":{"login":"octo"},"html_url":"https://github.com/octo/demo","default_branch":"main","stargazers_count":5}]}'

        parser = target.build_parser()
        args = parser.parse_args(["github-search", "--query", "agent memory", "--metadata", "unused.json"])
        rows, metadata = target.discover("github-search", args, FakeFetcher())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["entity"]["default_branch_commit_status"], "unavailable")
        self.assertFalse(metadata["commit_enrichment"])

    def test_github_pushed_window_builds_explicit_activity_query(self):
        class FakeFetcher:
            def __init__(self): self.calls = []
            def github(self, endpoint, params):
                self.calls.append((endpoint, params))
                return b'{"total_count":0,"items":[]}'

        parser = target.build_parser()
        args = parser.parse_args(["github-search", "--query", "agent memory", "--from", "2026-05-01", "--to", "2026-08-01", "--github-date-field", "pushed", "--metadata", "unused.json"])
        fetcher = FakeFetcher()
        _, metadata = target.discover("github-search", args, fetcher)
        query = fetcher.calls[0][1]["q"]
        self.assertIn("pushed:2026-05-01..2026-08-01", query)
        self.assertNotIn("created:", query)
        self.assertEqual(metadata["github_date_field"], "pushed")

    def test_merge_preserves_cross_provider_occurrences_and_removes_only_exact_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); input_path = root / "in.jsonl"; output = root / "out.jsonl"; metadata = root / "run.json"
            first = {"provider":"crossref","raw_id":"a","entity":{"kind":"paper","doi":"10/x"}}
            second = {"provider":"semantic-scholar","raw_id":"b","entity":{"kind":"paper","doi":"10/X"}}
            input_path.write_text('\n'.join([json.dumps(first), json.dumps(second), json.dumps(first)]) + '\n', encoding="utf-8")
            self.assertEqual(target.main(["merge", "--input", str(input_path), "--output", str(output), "--metadata", str(metadata)]), 0)
            self.assertEqual(len(output.read_text(encoding="utf-8").splitlines()), 2)
            saved = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(saved["occurrence_count"], 2)
            self.assertEqual(saved["exact_duplicate_occurrences_removed"], 1)

    def test_selected_repository_observation_is_complete_and_replayable(self):
        class FakeFetcher:
            def github(self, endpoint, params):
                fixtures = {
                    "/repos/octo/demo": {"id":1,"node_id":"R1","full_name":"octo/demo","default_branch":"main","created_at":"2020-01-02T00:00:00Z","pushed_at":"2026-08-01T00:00:00Z","stargazers_count":9,"forks_count":2,"open_issues_count":3,"archived":False,"fork":False,"license":{"spdx_id":"MIT"}},
                    "/repos/octo/demo/releases": [{"published_at":"2026-07-01T00:00:00Z"}],
                    "/repos/octo/demo/commits/main": {"sha":"tip123"},
                    "/repos/octo/demo/commits": [
                        {"sha":"c1","author":{"login":"ada"},"commit":{"author":{"email":"ada@example.test"}}},
                        {"sha":"c2","author":None,"commit":{"author":{"email":"grace@example.test"}}},
                    ],
                }
                return json.dumps(fixtures[endpoint]).encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = target.build_parser().parse_args(["github-observe", "--repo", "octo/demo", "--from", "2026-05-01", "--to", "2026-08-01", "--window-id", "W90", "--raw-dir", str(root / "raw"), "--output", str(root / "out.jsonl"), "--metadata", str(root / "run.json")])
            rows, metadata = target.observe_github(args, FakeFetcher())
            self.assertEqual(rows[0]["commits_in_window"], 2)
            self.assertEqual(rows[0]["contributors_in_window"], 2)
            self.assertEqual(rows[0]["default_commit"], "tip123")
            self.assertEqual(rows[0]["latest_release"], "2026-07-01")
            self.assertEqual(len(metadata["requests"]), 4)
            for request in metadata["requests"]:
                self.assertTrue(request["retrieved_at"].endswith("Z"))
                self.assertTrue(Path(request["raw_snapshot_path"]).is_file())
                self.assertTrue(request["response_sha256"])

    def test_selected_repository_observation_missing_counter_fails_not_zero(self):
        class FakeFetcher:
            def github(self, endpoint, params):
                fixtures = {
                    "/repos/octo/demo": {"id":1,"node_id":"R1","full_name":"octo/demo","default_branch":"main","created_at":"2020-01-02T00:00:00Z","pushed_at":"2026-08-01T00:00:00Z","stargazers_count":9,"forks_count":2,"archived":False,"fork":False},
                    "/repos/octo/demo/releases": [],
                    "/repos/octo/demo/commits/main": {"sha":"tip123"},
                    "/repos/octo/demo/commits": [],
                }
                return json.dumps(fixtures[endpoint]).encode("utf-8")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = target.build_parser().parse_args(["github-observe", "--repo", "octo/demo", "--from", "2026-05-01", "--to", "2026-08-01", "--window-id", "W90", "--raw-dir", str(root / "raw"), "--output", str(root / "out.jsonl"), "--metadata", str(root / "run.json")])
            with self.assertRaisesRegex(target.DiscoveryError, "refusing to encode unknown as zero"):
                target.observe_github(args, FakeFetcher())

    @patch.object(target.Fetcher, "http", return_value=b'{"message":{"total-results":0,"items":[]}}')
    def test_crossref_discovery_is_replayable(self, mocked_http):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); output = root / "out.jsonl"; metadata = root / "run.json"; raw_dir = root / "raw"
            self.assertEqual(target.main(["crossref", "--query", "test", "--from", "2024-01-01", "--to", "2024-12-31", "--limit", "1", "--output", str(output), "--metadata", str(metadata), "--raw-dir", str(raw_dir)]), 0)
            saved = json.loads(metadata.read_text(encoding="utf-8")); request = saved["requests"][0]
            self.assertEqual(request["provider"], "crossref"); self.assertTrue(request["response_sha256"]); self.assertTrue(Path(request["raw_snapshot_path"]).is_file())
            self.assertIn("from-pub-date", request["params"]["filter"])


if __name__ == "__main__":
    unittest.main()
