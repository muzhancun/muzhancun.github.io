#!/usr/bin/env python3
"""Sync link-page paper recommendations from Google Scholar.

The curated public/link-papers.json file is treated as the static fallback.
This script writes public/link-papers.live.json only when at least one Scholar
profile is fetched successfully.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FALLBACK_PATH = ROOT / "public" / "link-papers.json"
DEFAULT_OUTPUT_PATH = ROOT / "public" / "link-papers.live.json"
SCHOLAR_CITATION_URL = (
    "https://scholar.google.com/citations?"
    "view_op=view_citation&hl=en&user={scholar_id}&citation_for_view={citation_id}"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update public/link-papers.live.json from Google Scholar."
    )
    parser.add_argument(
        "--fallback",
        type=Path,
        default=DEFAULT_FALLBACK_PATH,
        help="Static fallback JSON with people and Scholar profile URLs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Generated Scholar-synced JSON path.",
    )
    parser.add_argument(
        "--no-promote-fallback",
        action="store_true",
        help="Do not also update the static fallback JSON after a successful sync.",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=0,
        help="Maximum papers per author. Use 0 to keep all publications.",
    )
    parser.add_argument(
        "--detail-limit",
        type=int,
        default=8,
        help="Maximum publication detail pages to fetch per author. Use 0 to skip.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds to sleep between Scholar requests.",
    )
    return parser.parse_args()


def load_scholarly() -> Any:
    try:
        from scholarly import scholarly
    except ImportError as exc:
        message = (
            "Missing dependency: scholarly. Install it with "
            "`python3 -m pip install -r scripts/requirements-scholar.txt`."
        )
        raise SystemExit(message) from exc

    return scholarly


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=True)
        file.write("\n")
    temp_path.replace(path)


def scholar_id_from_url(url: str) -> str | None:
    match = re.search(r"[?&]user=([^&]+)", url)
    return match.group(1) if match else None


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.casefold()).strip()


def fallback_paper_map(person: dict[str, Any]) -> dict[str, dict[str, Any]]:
    papers = person.get("papers")
    if not isinstance(papers, list):
        return {}

    return {
        normalize_title(str(paper.get("title", ""))): paper
        for paper in papers
        if isinstance(paper, dict) and paper.get("title")
    }


def scholar_citation_url(scholar_id: str, publication: dict[str, Any]) -> str:
    citation_id = publication.get("author_pub_id")
    if citation_id:
        return SCHOLAR_CITATION_URL.format(
            scholar_id=scholar_id,
            citation_id=citation_id,
        )

    return f"https://scholar.google.com/citations?user={scholar_id}"


def clean_citation(citation: str) -> str:
    citation = citation.replace("\u2026", "").replace("...", "")
    citation = re.sub(r"\s+", " ", citation).strip(" ,")
    return citation


def paper_venue(bib: dict[str, Any], fallback: dict[str, Any] | None) -> str:
    if fallback and fallback.get("venue"):
        return str(fallback["venue"])

    venue = bib.get("conference") or bib.get("journal") or bib.get("citation")
    year = bib.get("pub_year")

    if venue:
        venue_text = clean_citation(str(venue))
        year_text = str(year) if year else ""
        if year_text and year_text not in venue_text:
            return f"{venue_text} {year_text}"
        return venue_text

    return f"Google Scholar {year}" if year else "Google Scholar"


def paper_url(
    scholar_id: str,
    publication: dict[str, Any],
    fallback: dict[str, Any] | None,
) -> str:
    if fallback and fallback.get("url"):
        return str(fallback["url"])

    for key in ("pub_url", "eprint_url"):
        url = publication.get(key)
        if url:
            return str(url)

    return scholar_citation_url(scholar_id, publication)


def publication_to_paper(
    scholar_id: str,
    publication: dict[str, Any],
    fallback_by_title: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    bib = publication.get("bib")
    if not isinstance(bib, dict):
        return None

    title = bib.get("title")
    if not title:
        return None

    fallback = fallback_by_title.get(normalize_title(str(title)))
    paper: dict[str, Any] = {
        "title": str(title),
        "venue": paper_venue(bib, fallback),
        "url": paper_url(scholar_id, publication, fallback),
    }

    citations = publication.get("num_citations")
    if isinstance(citations, int):
        paper["citations"] = citations

    year = bib.get("pub_year")
    if year:
        paper["year"] = int(year) if str(year).isdigit() else str(year)

    return paper


def sync_person(
    scholarly: Any,
    person: dict[str, Any],
    max_papers: int,
    detail_limit: int,
    sleep_seconds: float,
) -> tuple[dict[str, Any], bool]:
    name = str(person.get("name", "Unknown"))
    scholar = str(person.get("scholar", ""))
    scholar_id = scholar_id_from_url(scholar)

    if not scholar_id:
        print(f"skip {name}: missing Scholar id")
        return person, False

    print(f"fetch {name} ({scholar_id})", flush=True)
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["basics", "publications"])
    publications = author.get("publications") or []
    if max_papers > 0:
        publications = publications[:max_papers]

    fallback_by_title = fallback_paper_map(person)
    papers: list[dict[str, Any]] = []
    details_used = 0

    for publication in publications:
        if detail_limit > 0 and details_used < detail_limit:
            try:
                publication = scholarly.fill(publication)
                details_used += 1
                time.sleep(sleep_seconds)
            except Exception as exc:  # noqa: BLE001
                title = publication.get("bib", {}).get("title", "unknown title")
                print(f"  detail fallback for {title}: {exc}", flush=True)

        paper = publication_to_paper(scholar_id, publication, fallback_by_title)
        if paper:
            papers.append(paper)

    if not papers:
        print(f"  no papers fetched for {name}; keeping fallback", flush=True)
        return person, False

    synced = {
        "name": name,
        "scholar": scholar,
        "papers": papers,
    }
    print(f"  synced {len(papers)} papers", flush=True)
    return synced, True


def main() -> int:
    args = parse_args()
    scholarly = load_scholarly()
    fallback = read_json(args.fallback)
    people = fallback.get("people", [])

    if not isinstance(people, list):
        print(f"{args.fallback} must contain a people array", file=sys.stderr)
        return 2

    synced_people: list[dict[str, Any]] = []
    success_count = 0

    for person in people:
        if not isinstance(person, dict):
            continue

        try:
            synced_person, ok = sync_person(
                scholarly,
                person,
                max_papers=args.max_papers,
                detail_limit=args.detail_limit,
                sleep_seconds=args.sleep,
            )
            success_count += int(ok)
        except Exception as exc:  # noqa: BLE001
            print(f"fallback {person.get('name', 'Unknown')}: {exc}", flush=True)
            synced_person = person

        synced_people.append(synced_person)
        time.sleep(args.sleep)

    if success_count == 0:
        print("No Scholar profiles synced; leaving generated JSON unchanged.")
        return 1

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "scholarly",
        "fallback": str(args.fallback.relative_to(ROOT)),
        "people": synced_people,
    }
    write_json_atomic(args.output, output)
    print(f"wrote {args.output.relative_to(ROOT)} with {success_count} synced profiles")
    if not args.no_promote_fallback:
        fallback_output = {
            "generatedAt": output["generatedAt"],
            "source": output["source"],
            "people": output["people"],
        }
        write_json_atomic(args.fallback, fallback_output)
        print(f"updated fallback {args.fallback.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
