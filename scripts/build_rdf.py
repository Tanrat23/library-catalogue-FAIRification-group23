#!/usr/bin/env python3
"""
build_rdf.py  -  turn the cleaned library CSV into RDF (Turtle).

One CSV row  ->  one lib:LibraryBook with its own URI.
Repeated values (authors, genres, sections) become shared resources, so
"Agatha Christie" is ONE node that 65 books point to, not 65 copies of a string.

Blank CSV cell  ->  no triple at all (RDF has no "empty": a missing fact is simply absent).

Usage:
  python scripts/build_rdf.py data/library_catalogue_repaired.csv data/rdf/library.ttl
  python scripts/build_rdf.py IN.csv OUT.ttl --base https://w3id.org/FAIR-course-UT/2026/group23/ --links data/openlibrary_links.csv
"""
import argparse, csv, hashlib, re, sys, unicodedata, datetime
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, SKOS

SCHEMA = Namespace("https://schema.org/")
THIS_YEAR = datetime.date.today().year

# Words that make us type an "author" as an Organization instead of a Person.
# It is a heuristic: the list of matches is printed at the end so you can eyeball it.
ORG_HINTS = re.compile(
    r"\b(congress|committee|commission|society|office|organisation|organization|academy|"
    r"collection|england and wales|department|ministry|university|institute|association|"
    r"council|bureau|board|staff|agency|government|library|museum|company|corporation|"
    r"foundation|league|federation|college|school|fund|press|publishers?|dept|church|editors)\b",
    re.I,
)
# Single-word bodies the keyword list cannot catch (states, countries, a publisher, an automobile club).
ORG_EXACT = {"AAA", "Bernan", "Boston", "Brazil", "Massachusetts", "Mexico", "Montana", "Newmarket"}
# "Anonymous" means "author unknown": we publish NO author triple for it, instead of inventing one person
# that dozens of unrelated books would all point to.
UNKNOWN_AUTHOR = {"anonymous"}


def slugify(text):
    """'Religion & Spirituality' -> 'religion-spirituality' (ASCII, lowercase, hyphens)."""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t


class SlugRegistry:
    """Gives each distinct label a stable slug; adds a short hash only on a clash or an empty slug."""

    def __init__(self):
        self.by_slug = {}

    def get(self, label):
        s = slugify(label)
        short = hashlib.sha1(label.encode("utf-8")).hexdigest()[:8]
        if not s:
            s = short  # e.g. a name written only in Cyrillic
        elif s in self.by_slug and self.by_slug[s] != label:
            s = f"{s}-{short}"
        self.by_slug[s] = label
        return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_in")
    ap.add_argument("ttl_out")
    ap.add_argument("--base", default="https://w3id.org/FAIR-course-UT/2026/group23/",
                    help="W3ID base; must end with a slash")
    ap.add_argument("--links", help="optional openlibrary_links.csv from link_openlibrary.py")
    args = ap.parse_args()

    base = args.base if args.base.endswith("/") else args.base + "/"
    LIB = Namespace(base + "ont#")
    DATA = Namespace(base + "data#")

    g = Graph()
    g.bind("lib", LIB)
    g.bind("data", DATA)
    g.bind("schema", SCHEMA)
    g.bind("skos", SKOS)
    g.bind("xsd", XSD)

    # optional external links
    links = {}
    if args.links:
        with open(args.links, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("work_key"):
                    links[r["catalogue_position"]] = r

    # the two controlled vocabularies
    genre_scheme, section_scheme = DATA["scheme-genres"], DATA["scheme-sections"]
    g.add((genre_scheme, RDF.type, SKOS.ConceptScheme))
    g.add((genre_scheme, SKOS.prefLabel, Literal("Library genres", lang="en")))
    g.add((section_scheme, RDF.type, SKOS.ConceptScheme))
    g.add((section_scheme, SKOS.prefLabel, Literal("Library sections", lang="en")))

    slugs = {"author": SlugRegistry(), "genre": SlugRegistry(), "section": SlugRegistry()}
    made = {"author": {}, "genre": {}, "section": {}}
    org_names, stats = [], {"books": 0, "year_dropped": 0, "linked_books": 0, "anonymous_skipped": 0}

    def get_author(name):
        if name in made["author"]:
            return made["author"][name]
        iri = DATA["author-" + slugs["author"].get(name)]
        made["author"][name] = iri
        is_org = bool(ORG_HINTS.search(name)) or name.rstrip(".") in ORG_EXACT
        g.add((iri, RDF.type, SCHEMA.Organization if is_org else SCHEMA.Person))
        g.add((iri, SCHEMA.name, Literal(name)))
        if is_org:
            org_names.append(name)
        return iri

    def get_concept(kind, label):
        if label in made[kind]:
            return made[kind][label]
        iri = DATA[f"{kind}-" + slugs[kind].get(label)]
        made[kind][label] = iri
        g.add((iri, RDF.type, LIB.Genre if kind == "genre" else LIB.Section))
        g.add((iri, SKOS.prefLabel, Literal(label, lang="en")))
        g.add((iri, SKOS.inScheme, genre_scheme if kind == "genre" else section_scheme))
        return iri

    with open(args.csv_in, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            pos = r["catalogue_position"].strip()
            book = DATA["book-" + pos]
            stats["books"] += 1

            g.add((book, RDF.type, LIB.LibraryBook))
            g.add((book, RDF.type, SCHEMA.Book))  # also typed directly, so plain Schema.org consumers see it
            g.add((book, LIB.cataloguePosition, Literal(pos)))

            if r["title"].strip():
                g.add((book, SCHEMA.name, Literal(r["title"].strip())))

            if r["author"].strip():
                names = [n.strip() for n in r["author"].split(" & ")]  # only the explicit "A & B" case
                for n in names:
                    if n.lower() in UNKNOWN_AUTHOR:
                        stats["anonymous_skipped"] += 1
                        continue
                    g.add((book, SCHEMA.author, get_author(n)))

            y = r["year_published"].strip()
            if y:
                yi = int(float(y))
                if 0 < yi <= THIS_YEAR:
                    g.add((book, SCHEMA.datePublished, Literal(str(yi), datatype=XSD.gYear)))
                else:
                    stats["year_dropped"] += 1

            if r["genre"].strip():
                g.add((book, SCHEMA.genre, get_concept("genre", r["genre"].strip())))
            if r["section"].strip():
                g.add((book, LIB.inSection, get_concept("section", r["section"].strip())))

            if r["times_borrowed"].strip():
                g.add((book, LIB.timesBorrowed,
                       Literal(int(float(r["times_borrowed"])), datatype=XSD.nonNegativeInteger)))

            if r["ratings"].strip() or r["ratings_count"].strip():
                rating = BNode()
                g.add((book, SCHEMA.aggregateRating, rating))
                g.add((rating, RDF.type, SCHEMA.AggregateRating))
                if r["ratings"].strip():
                    g.add((rating, SCHEMA.ratingValue, Literal(r["ratings"].strip(), datatype=XSD.decimal)))
                if r["ratings_count"].strip():
                    g.add((rating, SCHEMA.ratingCount, Literal(int(float(r["ratings_count"])), datatype=XSD.integer)))
                g.add((rating, SCHEMA.bestRating, Literal(5, datatype=XSD.integer)))
                g.add((rating, SCHEMA.worstRating, Literal(1, datatype=XSD.integer)))

            if r["price"].strip():
                g.add((book, LIB.price, Literal(r["price"].strip(), datatype=XSD.decimal)))
            if r["language"].strip():
                g.add((book, SCHEMA.inLanguage, Literal(r["language"].strip())))
            if r["isbn"].strip():
                g.add((book, LIB.recordedIsbn, Literal(r["isbn"].strip())))
            if r["subjects"].strip():
                g.add((book, SCHEMA.keywords, Literal(r["subjects"].strip())))

            # optional link to Open Library
            lk = links.get(pos)
            if lk:
                stats["linked_books"] += 1
                g.add((book, SCHEMA.sameAs, URIRef(f"https://openlibrary.org/works/{lk['work_key']}")))
                if lk.get("author_key") and r["author"].strip() and " & " not in r["author"]:
                    g.add((get_author(r["author"].strip()), SCHEMA.sameAs,
                           URIRef(f"https://openlibrary.org/authors/{lk['author_key']}")))

    g.serialize(destination=args.ttl_out, format="turtle")

    n = lambda cls: len(set(g.subjects(RDF.type, cls)))
    print(f"wrote {args.ttl_out}")
    print(f"  triples            : {len(g)}")
    print(f"  books              : {stats['books']}")
    print(f"  authors (persons)  : {n(SCHEMA.Person)}")
    print(f"  authors (orgs)     : {n(SCHEMA.Organization)}")
    print(f"  genres / sections  : {n(LIB.Genre)} / {n(LIB.Section)}")
    print(f"  years dropped (> {THIS_YEAR}): {stats['year_dropped']}")
    print(f"  'Anonymous' authors left out : {stats['anonymous_skipped']}")
    if args.links:
        print(f"  books linked to Open Library: {stats['linked_books']}")
    print(f"  organisation-typed authors to eyeball ({len(org_names)}):")
    for name in org_names:
        print("     -", name)


if __name__ == "__main__":
    sys.exit(main())
