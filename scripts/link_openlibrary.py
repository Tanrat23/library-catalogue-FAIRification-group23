#!/usr/bin/env python3
"""
link_openlibrary.py  -  find each catalogue book's "twin" in Open Library.

For every row we ask Open Library's search API for the title + author, accept a hit only when
BOTH the title and the author agree, and write the match to a CSV. build_rdf.py then turns each
match into   <our book> schema:sameAs <https://openlibrary.org/works/OL...W>.
We store only the LINK (an identifier), never Open Library's own data.

Politeness (Open Library asks for this): identify yourself and stay under 3 requests per second.
Results are cached, so you can stop (Ctrl+C) and re-run; it continues where it stopped.

Usage:
  python scripts/link_openlibrary.py data/library_catalogue_repaired.csv \
         data/openlibrary_links.csv --email you@example.org
  add  --limit 40   for a quick trial on the first 40 rows
"""
import argparse, csv, json, os, random, re, sys, time, unicodedata, urllib.parse, urllib.request, urllib.error
from difflib import SequenceMatcher

API = "https://openlibrary.org/search.json"
FIELDS = "key,title,author_name,author_key,first_publish_year"
TITLE_THRESHOLD = 0.90


def norm(s):
    """lowercase, ASCII, drop (1st Edition) and subtitles, drop punctuation and a leading article"""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = s.split(":")[0]
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)


def surname(s):
    t = norm(s).split()
    return t[-1] if t else ""


def author_ok(csv_author, candidate_names):
    if not csv_author:
        return True  # nothing to compare; title alone decides
    want = norm(csv_author)
    for name in candidate_names or []:
        if surname(name) == surname(csv_author) or SequenceMatcher(None, norm(name), want).ratio() >= 0.85:
            return True
    return False


def pick_match(title, author, docs):
    """best doc whose title AND author agree, or None"""
    best, best_score = None, 0.0
    for d in docs:
        score = SequenceMatcher(None, norm(title), norm(d.get("title", ""))).ratio()
        if score >= TITLE_THRESHOLD and author_ok(author, d.get("author_name")) and score > best_score:
            best, best_score = d, score
    return best, best_score


def fetch(url, user_agent, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            time.sleep(30 if e.code == 429 else 2 * (attempt + 1))
        except Exception:  # network hiccup
            time.sleep(2 * (attempt + 1))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_in")
    ap.add_argument("links_out")
    ap.add_argument("--email", required=True, help="put in the User-Agent so Open Library can contact you")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=0.5, help="seconds between requests (0.5 = 2 per second)")
    ap.add_argument("--cache", default=os.path.join(os.path.expanduser("~"), ".fair-group23-openlibrary-cache.json"),
                    help="lookup cache; kept in your home folder so it never ends up in the repository")
    args = ap.parse_args()

    ua = f"LibraryFAIRProject/0.1 ({args.email})"
    cache = json.load(open(args.cache, encoding="utf-8")) if os.path.exists(args.cache) else {}

    with open(args.csv_in, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[: args.limit]

    out, n_new = [], 0
    for i, r in enumerate(rows, 1):
        pos, title, author = r["catalogue_position"], r["title"].strip(), r["author"].strip()
        if pos not in cache:
            q = {"title": title, "limit": 5, "fields": FIELDS}
            if author and author.lower() != "anonymous":
                q["author"] = author
            data = fetch(f"{API}?{urllib.parse.urlencode(q)}", ua)
            cache[pos] = None if data is None else data.get("docs", [])
            n_new += 1
            time.sleep(args.delay)
            if n_new % 25 == 0:
                json.dump(cache, open(args.cache, "w", encoding="utf-8"))
                print(f"  {i}/{len(rows)} rows done", flush=True)

        docs = cache[pos]
        if docs is None:
            out.append({"catalogue_position": pos, "title": title, "author": author, "status": "error"})
            continue
        hit, score = pick_match(title, author, docs)
        if hit:
            names, keys = hit.get("author_name") or [], hit.get("author_key") or []
            idx = next((j for j, n in enumerate(names) if author_ok(author, [n])), 0)
            out.append({
                "catalogue_position": pos, "title": title, "author": author,
                "work_key": hit["key"].replace("/works/", ""),
                "matched_title": hit.get("title", ""),
                "matched_author": names[idx] if names else "",
                "author_key": (keys[idx] if keys else "").replace("/authors/", ""),
                "first_publish_year": hit.get("first_publish_year", ""),
                "score": round(score, 3), "status": "matched",
            })
        else:
            out.append({"catalogue_position": pos, "title": title, "author": author, "status": "no_match"})

    json.dump(cache, open(args.cache, "w", encoding="utf-8"))
    cols = ["catalogue_position", "title", "author", "work_key", "matched_title", "matched_author",
            "author_key", "first_publish_year", "score", "status"]
    with open(args.links_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    matched = [o for o in out if o["status"] == "matched"]
    errors = sum(1 for o in out if o["status"] == "error")
    print(f"\nrows checked : {len(out)}")
    print(f"matched      : {len(matched)}  ({100 * len(matched) / max(1, len(out)):.1f}% coverage)")
    print(f"no match     : {len(out) - len(matched) - errors}")
    print(f"errors       : {errors}  (re-run to retry)")

    # a random sample for the by-hand precision check
    sample_path = os.path.splitext(args.links_out)[0] + "_review_sample.csv"
    sample = random.Random(42).sample(matched, min(30, len(matched)))
    with open(sample_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols + ["correct_yes_no"], lineterminator="\n")
        w.writeheader()
        for s in sample:
            w.writerow({**s, "correct_yes_no": ""})
    print(f"review sample: {sample_path}  (open each work page and fill correct_yes_no)")


if __name__ == "__main__":
    sys.exit(main())
