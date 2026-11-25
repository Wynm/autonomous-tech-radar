#!/usr/bin/env python3
"""
Marginalia Niche Research & Intelligence SaaS Core
A zero-dependency Python tool to query, analyze, and aggregate non-commercial web content.
"""

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter


class MarginaliaResearchEngine:
    """Core engine for fetching and processing non-commercial search insights."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def fetch_and_analyze(self, query: str, limit: int = 5, mock_data: dict = None) -> dict:
        """Fetch search results and compute content analysis metrics."""
        if mock_data is not None:
            raw_data = mock_data
        else:
            raw_data = self._remote_fetch(query)

        results = raw_data.get("results", [])[:limit]
        analyzed_items = []
        word_pool = []

        for item in results:
            title = item.get("title", "Untitled")
            snippet = item.get("snippet", "") or item.get("description", "")
            url = item.get("url", "")

            # Process text content (Standard Lib NLP)
            words = re.findall(r"\b[a-zA-Z]{4,}\b", snippet.lower())
            word_pool.extend(words)

            analyzed_items.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "word_count": len(snippet.split()),
                "est_read_time_sec": max(5, len(snippet.split()) * 2)
            })

        # Extract top key concepts
        top_concepts = [word for word, _ in Counter(word_pool).most_common(5)]

        return {
            "status": "success",
            "query": query,
            "total_extracted": len(analyzed_items),
            "top_concepts": top_concepts,
            "digest": analyzed_items
        }

    def _remote_fetch(self, query: str) -> dict:
        """Fetch live results via Marginalia public search API endpoint."""
        encoded_query = urllib.parse.quote(query)
        target_url = f"https://api.marginalia.nu/public/search/{encoded_query}"
        req = urllib.request.Request(
            target_url,
            headers={"User-Agent": "MarginaliaSaaSAgent/1.0"}
        )

        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
        except Exception as err:
            return {"error": str(err), "results": []}

        return {"results": []}


def run_self_test() -> bool:
    """Executes clean self-test without external network or system side-effects."""
    print("=== [RUNNING SELF-TEST] ===")

    mock_response = {
        "results": [
            {
                "title": "Minimalist Web Architecture",
                "url": "https://example.org/minimalist-architecture",
                "snippet": "A deep dive into high-performance web engines built with Rust and C++ avoiding bloat."
            },
            {
                "title": "Independent Search Engines",
                "url": "https://example.org/indie-search",
                "snippet": "Why non-commercial web indexing preserves technical depth and original blogging."
            }
        ]
    }

    engine = MarginaliaResearchEngine()
    output = engine.fetch_and_analyze(query="independent search", limit=2, mock_data=mock_response)

    # Assertions
    assert output["status"] == "success", "Test Failed: Status must be success"
    assert output["total_extracted"] == 2, f"Test Failed: Expected 2 items, got {output['total_extracted']}"
    assert len(output["top_concepts"]) > 0, "Test Failed: Concepts extraction failed"
    assert output["digest"][0]["word_count"] > 0, "Test Failed: Word count calculation failed"

    print(json.dumps(output, indent=2))
    print("=== [SELF-TEST PASSED SUCCESSFULLY] ===")
    return True


def main():
    parser = argparse.ArgumentParser(description="Marginalia Niche Content Aggregator & SaaS Core")
    parser.add_argument("--query", type=str, help="Research topic or search query")
    parser.add_argument("--limit", type=int, default=5, help="Number of results to analyze")
    parser.add_argument("--self-test", action="store_true", help="Run automated self-test and exit")

    args = parser.parse_args()

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    engine = MarginaliaResearchEngine()
    result = engine.fetch_and_analyze(query=args.query, limit=args.limit)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
