#!/usr/bin/env python3
"""
search_patterns.py — cross-reference a candidate finding against the known
vulnerability-pattern index built from ~900 past audit findings.

Usage:
    python3 search_patterns.py "createAndInitializePoolIfNecessary no slippage on mint"
    python3 search_patterns.py --file /path/to/Contract.sol
    python3 search_patterns.py "reward rate change" --top 5

Output: ranked list of pattern IDs with the reference file to open next.
This is a cheap pre-filter, not a verdict — always read the matched
reference file(s) before writing up or dismissing a finding.
"""
import json
import os
import re
import sys
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(HERE, "..", "pattern_index.json")


def load_index():
    with open(INDEX_PATH, "r") as f:
        return json.load(f)


def tokenize(text):
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


STOPWORDS = {"a", "an", "the", "of", "on", "in", "to", "is", "not", "no", "or", "and"}


def looks_like_identifier(kw):
    """True for code-identifier-shaped keywords (camelCase, snake_case,
    dotted calls) as opposed to a plain English word. Used to gate the
    single-hit floor below: an exact match on 'onFlashLoan' or
    '_requireOwned' is strong evidence on its own; an exact match on a
    plain word like 'graduate' or 'pool' is not, even though both score
    the same 'single-word substring' raw points. Without this gate, the
    fix for the original keyword-count bias (see score_pattern's
    docstring) would let a pattern with one generic single-word keyword
    get an undeserved floor just from that word appearing in an unrelated
    query."""
    return bool(re.search(r"[_.]", kw)) or bool(re.search(r"[a-z][A-Z]", kw))


def score_pattern(query_tokens, query_text_lower, pattern):
    """Returns (combined_score, normalized_score, raw_score, hits).

    normalized_score is raw_score / number_of_keywords_in_this_pattern.
    Without this normalization, a pattern with many keywords structurally
    out-scores a pattern with few keywords on generic/partial overlap alone,
    even when the few-keyword pattern is the better conceptual match — e.g.
    a 9-keyword pattern racking up two 0.5-overlap partial hits on generic
    DeFi vocabulary ("pool", "seed", "liquidity") beat a 3-keyword pattern
    that's the actual right answer, on a query that had nothing to do with
    pools at all. Normalizing turns the score into "what fraction of this
    pattern's defining vocabulary did the query hit," which is comparable
    across patterns regardless of how many keywords each one happens to
    have. See references/source-log.md changelog for the worked example.

    That fix has its own side effect: a pattern with several keyword
    *phrases* covering different ways to describe the same thing (which is
    normal — most patterns have 2-5 keyword variants) gets a single
    excellent hit diluted toward zero by the other, unmatched phrases,
    even though one exact hit on a specific phrase is often all the
    evidence you need. `single_hit_floor` fixes this: an exact substring
    match on a multi-word phrase, or on a single word that looks like a
    code identifier (`looks_like_identifier`), sets a floor under the
    combined score regardless of how many other keywords on the same
    pattern missed. Plain single-word matches (no code-identifier shape)
    don't get a floor — those are exactly the generic terms ("pool",
    "seed", "graduate") the normalization fix above was written to stop
    from carrying undue weight.
    """
    raw = 0
    single_hit_floor = 0.0
    hits = []
    for kw in pattern["keywords"]:
        kw_l = kw.lower()
        if kw_l in query_text_lower:
            is_phrase = " " in kw_l
            contribution = 3 if is_phrase else 2
            raw += contribution
            hits.append(kw)
            if is_phrase or looks_like_identifier(kw):
                single_hit_floor = max(single_hit_floor, contribution / 2.0)
            continue
        kw_tokens = tokenize(kw) - STOPWORDS
        if not kw_tokens:
            continue
        overlap = kw_tokens & query_tokens
        if not overlap:
            continue
        frac = len(overlap) / len(kw_tokens)
        if frac == 1.0:
            raw += 1.5
            hits.append(kw)
            if len(kw_tokens) > 1:
                single_hit_floor = max(single_hit_floor, 1.5 / 2.0)
        elif frac >= 0.5:
            raw += 1
            hits.append(f"{kw} (partial)")
    normalized = raw / len(pattern["keywords"]) if pattern["keywords"] else 0
    combined = max(normalized, single_hit_floor)
    return combined, normalized, raw, hits


def strength_band(normalized):
    if normalized >= 1.5:
        return "strong"
    if normalized >= 0.6:
        return "moderate"
    return "weak"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", help="free-text description, function name, or code snippet")
    ap.add_argument("--file", help="read the query text from a file instead (e.g. a .sol file or a draft finding)")
    ap.add_argument("--top", type=int, default=8, help="max number of patterns to show (default 8)")
    ap.add_argument("--json", action="store_true", help="emit ranked matches as JSON")
    args = ap.parse_args()

    if args.file:
        with open(args.file, "r", errors="ignore") as f:
            query = f.read()
    elif args.query:
        query = args.query
    else:
        ap.print_help()
        sys.exit(1)

    idx = load_index()
    query_tokens = tokenize(query)
    query_lower = query.lower()

    results = []
    for cat in idx["categories"]:
        for pat in cat["patterns"]:
            combined, normalized, raw, hits = score_pattern(query_tokens, query_lower, pat)
            if combined > 0:
                results.append((combined, normalized, cat["file"], cat["title"], pat, hits))

    results.sort(key=lambda r: r[0], reverse=True)

    if not results:
        if args.json:
            print("[]")
        else:
            print("No keyword matches. This may be a novel pattern (good — write it up and add it to")
            print("pattern_index.json + the relevant references/*.md so future audits benefit), or try")
            print("re-running with different terms (function name, error message, root-cause verb like")
            print("'donation', 'replay', 'unbounded', 'rounds down', etc).")
        return

    if args.json:
        payload = []
        for combined, normalized, file, title, pat, hits in results[: args.top]:
            payload.append({
                "id": pat["id"],
                "name": pat["name"],
                "strength": strength_band(combined),
                "score": round(combined, 4),
                "normalized_score": round(normalized, 4),
                "category": title,
                "reference": f"references/{file}",
                "severity_seen": pat["severity_seen"],
                "matched": hits,
            })
        print(json.dumps(payload, indent=2))
        return

    print(f"Top {min(args.top, len(results))} candidate pattern(s) for: {query[:120]!r}\n")
    for combined, normalized, file, title, pat, hits in results[: args.top]:
        band = strength_band(combined)
        print(f"[{pat['id']}] {pat['name']}  ({band} match, score {combined:.2f})")
        print(f"    category : {title}")
        print(f"    severity : {', '.join(pat['severity_seen'])}")
        print(f"    matched  : {', '.join(hits)}")
        print(f"    read     : references/{file}")
        print()
    if results[0][0] < 0.6:
        print("Note: even the top match is 'weak.' Don't anchor on it — read the category table in")
        print("SKILL.md and open whichever reference file is closest by subject matter instead.")


if __name__ == "__main__":
    main()
