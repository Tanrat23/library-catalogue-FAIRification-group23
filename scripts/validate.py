#!/usr/bin/env python3
"""
validate.py  -  the quality gates for Person 2's deliverables.

  A. Syntax      every .ttl file parses
  B. Records     library.ttl conforms to shapes/book-shape.ttl (SHACL)
  C. URIs        hygiene checks on every IRI (namespace, no spaces, no dangling references,
                 every lib: term used is declared in the ontology, one book per CSV row)
  D. Metadata    metadata/dataset-record.ttl conforms to the Dataset and Distribution shapes
  E. Self-test   (--selftest) feeds deliberately broken records to the shapes and checks that
                 each one is REJECTED. A bouncer that never says no is not a bouncer.

Usage (from the repo root):
  python scripts/validate.py
  python scripts/validate.py --selftest
"""
import argparse, csv, os, re, sys
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, OWL
from pyshacl import validate as shacl_validate

SCHEMA = Namespace("https://schema.org/")
LIB = Namespace("https://w3id.org/FAIR-course-UT/2026/group23/ont#")
DATA = Namespace("https://w3id.org/FAIR-course-UT/2026/group23/data#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
TTL_DISTRIBUTION = URIRef("https://w3id.org/FAIR-course-UT/2026/group23/distribution/ttl")

FILES = {
    "ontology": "ontology/library-ontology.ttl",
    "data": "data/rdf/library.ttl",
    "book_shape": "shapes/book-shape.ttl",
    "dataset_shape": "shapes/dataset-shape.ttl",
    "distribution_shape": "shapes/distribution-shape.ttl",
    "metadata": "metadata/dataset-record.ttl",
}
CSV_PATH = "data/library_catalogue_repaired.csv"

failures = []


def report(ok, label, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def load(path):
    g = Graph()
    g.parse(path, format="turtle")
    return g


def shacl(data, shapes, ont=None):
    conforms, _, text = shacl_validate(data, shacl_graph=shapes, ont_graph=ont, inference="none")
    return conforms, text


def short_violations(text, n=5):
    return "; ".join(re.findall(r"Message: (.+)", text)[:n]) or text[:200]


# ------------------------------------------------------------------ A. syntax
def check_syntax():
    graphs = {}
    for key, path in FILES.items():
        try:
            graphs[key] = load(path)
            report(True, f"A. {path} parses", f"{len(graphs[key])} triples")
        except Exception as e:  # noqa
            report(False, f"A. {path} parses", str(e)[:120])
    return graphs


# ------------------------------------------------------------------ B. records vs book shape
def check_records(gr):
    ok, text = shacl(gr["data"], gr["book_shape"], gr["ontology"])
    report(ok, "B. library.ttl conforms to book-shape.ttl", "" if ok else short_violations(text))


# ------------------------------------------------------------------ C. URI hygiene
def check_uris(gr):
    data, ont = gr["data"], gr["ontology"]

    bad_ns = [s for s in set(data.subjects()) if isinstance(s, URIRef) and not str(s).startswith(str(DATA))]
    report(not bad_ns, "C1. every subject IRI lives in the data# namespace", f"{len(bad_ns)} outside")

    bad_chars = [s for s in set(data.subjects()) if isinstance(s, URIRef) and re.search(r"[\s<>\"{}|\\^`]", str(s))]
    report(not bad_chars, "C2. no illegal characters in any IRI", f"{len(bad_chars)} bad")

    dangling = []
    for pred in (SCHEMA.author, SCHEMA.genre, LIB.inSection):
        for o in set(data.objects(None, pred)):
            if (o, RDF.type, None) not in data:
                dangling.append(str(o))
    report(not dangling, "C3. no dangling references (author/genre/section all described)", f"{len(dangling)} dangling")

    used = {p for p in set(data.predicates()) | set(data.objects(None, RDF.type)) if str(p).startswith(str(LIB))}
    declared = set(ont.subjects(RDF.type, None))
    undeclared = sorted(str(t) for t in used if t not in declared)
    report(not undeclared, "C4. every lib: term used in the data is declared in the ontology", ", ".join(undeclared))

    books = set(data.subjects(RDF.type, LIB.LibraryBook))
    positions = [str(o) for o in data.objects(None, LIB.cataloguePosition)]
    report(len(positions) == len(set(positions)), "C5. catalogue positions are unique", f"{len(positions)} values")

    mism = [b for b in books if str(b) != str(DATA) + "book-" + str(data.value(b, LIB.cataloguePosition))]
    report(not mism, "C6. each book IRI is built from its catalogue position", f"{len(mism)} mismatches")

    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            n_rows = sum(1 for _ in csv.DictReader(f))
        report(len(books) == n_rows, "C7. number of books equals number of CSV rows", f"{len(books)} vs {n_rows}")
    except FileNotFoundError:
        report(False, "C7. CSV found for row count", CSV_PATH)


# ------------------------------------------------------------------ D. metadata shapes
def declared_size(meta):
    """the dcat:byteSize the metadata states for the RDF distribution (None if missing)"""
    v = meta.value(TTL_DISTRIBUTION, DCAT.byteSize)
    return int(v) if v is not None else None


def check_metadata(gr):
    ok, text = shacl(gr["metadata"], gr["dataset_shape"] + gr["distribution_shape"])
    report(ok, "D. dataset-record.ttl conforms to Dataset and Distribution shapes", "" if ok else short_violations(text))
    actual, declared = os.path.getsize(FILES["data"]), declared_size(gr["metadata"])
    report(declared == actual, "D2. dcat:byteSize of the RDF distribution equals the real file size",
           f"metadata says {declared}, file has {actual}")


# ------------------------------------------------------------------ E. self-test
BOOK_PREFIXES = """
@prefix lib: <https://w3id.org/FAIR-course-UT/2026/group23/ont#> .
@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix data: <https://w3id.org/FAIR-course-UT/2026/group23/data#> .
"""

GOOD_BOOK = BOOK_PREFIXES + """
data:genre-x a lib:Genre . data:author-x a schema:Person .
data:book-A1-B1-0001 a lib:LibraryBook ;
  lib:cataloguePosition "A1-B1-0001" ; schema:name "Enormous Room" ;
  schema:author data:author-x ; schema:genre data:genre-x ;
  schema:datePublished "1949"^^xsd:gYear ; lib:price 14.66 ;
  lib:timesBorrowed "3"^^xsd:nonNegativeInteger ; schema:inLanguage "en" .
"""


def selftest(gr):
    print("\nSelf-test: each broken record below MUST be rejected")

    def book_case(label, old, new):
        g = Graph().parse(data=GOOD_BOOK.replace(old, new), format="turtle")
        ok, _ = shacl(g, gr["book_shape"], gr["ontology"])
        report(not ok, f"E. book rejected: {label}")

    ok, _ = shacl(Graph().parse(data=GOOD_BOOK, format="turtle"), gr["book_shape"], gr["ontology"])
    report(ok, "E. a correct sample book is accepted")
    book_case("year 2999", '"1949"', '"2999"')
    book_case("negative price", "lib:price 14.66", "lib:price -3.0")
    book_case("title missing", 'schema:name "Enormous Room" ;', "")
    book_case("language in capitals", 'schema:inLanguage "en"', 'schema:inLanguage "EN"')
    book_case("author as plain text", "schema:author data:author-x", 'schema:author "E. E. Cummings"')
    book_case("bad catalogue position", 'lib:cataloguePosition "A1-B1-0001"', 'lib:cataloguePosition "1"')

    meta_text = open(FILES["metadata"], encoding="utf-8").read()
    shapes = gr["dataset_shape"] + gr["distribution_shape"]

    def meta_case(label, old, new, count=1):
        g = Graph().parse(data=meta_text.replace(old, new, count), format="turtle")
        ok, _ = shacl(g, shapes)
        report(not ok, f"E. metadata rejected: {label}")

    meta_case("dataset without licence", "    dcterms:license <https://spdx.org/licenses/MIT> ;\n    dcterms:publisher", "    dcterms:publisher")
    meta_case("dataset without keywords", '    dcat:keyword "library" , "catalogue" , "books" , "FAIR" , "Schema.org" ;\n', "")
    meta_case("distribution without media type",
              "    dcat:mediaType <https://www.iana.org/assignments/media-types/text/csv> ;\n", "", 1)
    meta_case("distribution without download URL",
              "    dcat:downloadURL <https://w3id.org/FAIR-course-UT/2026/group23/distribution/original-csv> ;\n", "")
    meta_case("media type as plain text", "dcat:mediaType <https://www.iana.org/assignments/media-types/text/turtle>",
              'dcat:mediaType "text/turtle"')
    actual = os.path.getsize(FILES["data"])
    wrong = Graph().parse(data=meta_text.replace(f'"{actual}"^^xsd:nonNegativeInteger', '"1"^^xsd:nonNegativeInteger'), format="turtle")
    report(declared_size(wrong) != actual, "E. metadata rejected: wrong byte size")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    gr = check_syntax()
    if len(gr) == len(FILES):
        check_records(gr)
        check_uris(gr)
        check_metadata(gr)
        if args.selftest:
            selftest(gr)

    print()
    if failures:
        print(f"{len(failures)} check(s) FAILED:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
