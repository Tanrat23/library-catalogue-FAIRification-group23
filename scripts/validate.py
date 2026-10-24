#!/usr/bin/env python3
"""
validate.py  -  the quality gates for Person 2's deliverables.

  A. Syntax      every .ttl file parses, including the three FAIR Data Point exports in metadata/
  B. Records     library.ttl conforms to shapes/book-shape.ttl (SHACL)
  C. URIs        hygiene checks on every IRI (namespace, no spaces, no dangling references,
                 every lib: term used is declared in the ontology, one book per CSV row)
  D. Shapes      our hand-written example record (shapes/test-fixtures/) conforms to the
                 Dataset and Distribution shapes
  F. FDP records the three FAIR Data Point exports in metadata/ (made by Person 1) carry what
                 the course asks for: persistent W3ID identifiers, working download links,
                 mailto: contact points, licence, publisher, and so on
  E. Self-test   (--selftest) feeds deliberately broken records to the checks and verifies that
                 each one is REJECTED. A bouncer that never says no is not a bouncer.

Lines marked WARN are not failures. They name things the FAIR Data Point schemas have to be
edited for (for example a media type stored as text instead of a link).

Usage (from the repo root):
  python scripts/validate.py
  python scripts/validate.py --selftest
"""
import argparse, csv, os, re, sys
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, OWL
from pyshacl import validate as shacl_validate

SCHEMA = Namespace("https://schema.org/")
LIB = Namespace("https://w3id.org/FAIR-course-UT/2026/group23/ont#")
DATA = Namespace("https://w3id.org/FAIR-course-UT/2026/group23/data#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
FDPO = Namespace("https://w3id.org/fdp/fdp-o#")

W3ID = "https://w3id.org/FAIR-course-UT/2026/group23/"
DATASET_ID = W3ID + "dataset"
CSV_ID = W3ID + "distribution/original-csv"
TTL_ID = W3ID + "distribution/ttl"
IANA = "https://www.iana.org/assignments/media-types/"
RULE_TESTS = "w3id/rules/FAIR-course-UT/2026/group23/tests.yaml"

FILES = {
    "ontology": "ontology/library-ontology.ttl",
    "data": "data/rdf/library.ttl",
    "book_shape": "shapes/book-shape.ttl",
    "dataset_shape": "shapes/dataset-shape.ttl",
    "distribution_shape": "shapes/distribution-shape.ttl",
    "fixture": "shapes/test-fixtures/dataset-record-draft.ttl",
    "fdp_dataset": "metadata/dataset-record.ttl",
    "fdp_csv": "metadata/distribution-original-csv.ttl",
    "fdp_ttl": "metadata/distribution-rdf.ttl",
}
CORE = ["ontology", "data", "book_shape", "dataset_shape", "distribution_shape", "fixture"]
CSV_PATH = "data/library_catalogue_repaired.csv"

failures = []
warnings = []


def report(ok, label, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))
    if not ok:
        failures.append(label)


def warn(message):
    print(f"[WARN] {message}")
    warnings.append(message)


def skip(label, why):
    print(f"[SKIP] {label}  ({why})")


def load(path):
    g = Graph()
    g.parse(path, format="turtle")
    return g


def shacl(data, shapes, ont=None):
    conforms, _, text = shacl_validate(data, shacl_graph=shapes, ont_graph=ont, inference="none")
    return conforms, text


def short_violations(text, n=5):
    return "; ".join(re.findall(r"Message: (.+)", text)[:n]) or text[:200]


def parse_error(e):
    """a short, readable version of a Turtle parse error"""
    s = str(e).replace("\n", " ")
    where = re.search(r"at line (\d+)", s)
    what = re.search(r"Bad syntax \(([^)]*)\)", s)
    if where and what:
        return f"line {where.group(1)}: {what.group(1)}"
    return s[:120]


# ------------------------------------------------------------------ A. syntax
def check_syntax():
    graphs = {}
    for key, path in FILES.items():
        try:
            graphs[key] = load(path)
            report(True, f"A. {path} parses", f"{len(graphs[key])} triples")
        except FileNotFoundError:
            report(False, f"A. {path} parses", "file not found")
        except Exception as e:  # noqa
            report(False, f"A. {path} parses", parse_error(e))
    return graphs


# ------------------------------------------------------------------ B. records vs book shape
def check_records(gr):
    ok, text = shacl(gr["data"], gr["book_shape"], gr["ontology"])
    report(ok, "B. library.ttl conforms to book-shape.ttl", "" if ok else short_violations(text))


def orphan_authors(graph):
    """Person or Organization nodes that no book points to (for example a link added to a left-out author)"""
    used = set(graph.objects(None, SCHEMA.author))
    nodes = set(graph.subjects(RDF.type, SCHEMA.Person)) | set(graph.subjects(RDF.type, SCHEMA.Organization))
    return sorted(nodes - used)


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

    orphans = orphan_authors(data)
    report(not orphans, "C8. every author node belongs to at least one book", f"{len(orphans)} orphans")


# ------------------------------------------------------------------ D. our example record vs our shapes
def check_shapes(gr):
    ok, text = shacl(gr["fixture"], gr["dataset_shape"] + gr["distribution_shape"])
    report(ok, "D. the example record conforms to the Dataset and Distribution shapes", "" if ok else short_violations(text))


# ------------------------------------------------------------------ F. the FAIR Data Point records
def show(v, n=70):
    """a value for a message: only the last part of a file path, line breaks made visible, cut when long"""
    s = str(v)
    if s.startswith("file:"):
        s = s.rsplit("/", 1)[-1]
    s = s.replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + "..."


def identifier_values(g, node):
    """the FDP keeps the identifier in a small sub-record: node fdpo:metadataIdentifier [ dcterms:identifier "..." ]"""
    values = []
    for ident in g.objects(node, FDPO.metadataIdentifier):
        values += [str(v) for v in g.objects(ident, DCT.identifier)]
    return values


def identifier_problem(values, expected):
    if not values:
        return "no identifier"
    if len(values) > 1:
        return f"{len(values)} identifiers"
    v = values[0]
    if v == expected:
        return None
    if re.search(r"\s", v):
        return f"identifier is not one clean link ({len(v)} characters, {v.count(chr(10)) + 1} lines), expected {expected}"
    return f"identifier is {show(v)}, expected {expected}"


def dataset_issues(g):
    """problems in the FDP dataset record, grouped under the check labels F1 to F3"""
    out = {"F1": [], "F2": [], "F3": []}
    found = sorted(g.subjects(RDF.type, DCAT.Dataset), key=str)
    if len(found) != 1:
        out["F1"].append(f"expected 1 dcat:Dataset, found {len(found)}")
        return out
    d = found[0]

    def need(pred, name, link=False):
        vals = list(g.objects(d, pred))
        if not vals:
            out["F1"].append(f"no {name}")
        elif link and not all(isinstance(v, URIRef) for v in vals):
            out["F1"].append(f"{name} must be a link")
        elif not link and not all(isinstance(v, Literal) and str(v).strip() for v in vals):
            out["F1"].append(f"{name} must be text")

    need(DCT.title, "title")
    need(DCT.description, "description")
    need(DCT.license, "licence", link=True)
    need(DCAT.keyword, "keyword")
    need(DCAT.landingPage, "landing page", link=True)
    need(DCAT.theme, "theme", link=True)
    need(DCT.language, "language", link=True)
    if not any(g.value(p, FOAF.name) for p in g.objects(d, DCT.publisher)):
        out["F1"].append("no publisher with a name")

    contacts = list(g.objects(d, DCAT.contactPoint))
    if not contacts:
        out["F2"].append("no contact point")
    for c in contacts:
        if not (isinstance(c, URIRef) and re.fullmatch(r"mailto:[^@\s]+@[^@\s]+\.[^@\s]+", str(c))):
            out["F2"].append(f"'{show(c)}' is not a mailto: link")

    problem = identifier_problem(identifier_values(g, d), DATASET_ID)
    if problem:
        out["F3"].append(problem)
    return out


def distribution_issues(g, expected):
    """problems in one FDP distribution record (list of messages, empty = fine)"""
    found = sorted(g.subjects(RDF.type, DCAT.Distribution), key=str)
    if len(found) != 1:
        return [f"expected 1 dcat:Distribution, found {len(found)}"]
    d, out = found[0], []
    if not any(str(v).strip() for v in g.objects(d, DCT.title)):
        out.append("no title")
    lic = list(g.objects(d, DCT.license))
    if not lic or not all(isinstance(v, URIRef) for v in lic):
        out.append("no licence link")
    problem = identifier_problem(identifier_values(g, d), expected)
    if problem:
        out.append(problem)
    for pred, name in ((DCAT.downloadURL, "download URL"), (DCAT.accessURL, "access URL")):
        vals = set(g.objects(d, pred))
        if vals != {URIRef(expected)}:
            out.append(f"{name} is {', '.join(show(v) for v in sorted(vals, key=str)) or 'missing'}, expected {expected}")
    return out


def distribution_warnings(g, name):
    """things the FDP schema has to be edited for: not failures"""
    found = sorted(g.subjects(RDF.type, DCAT.Distribution), key=str)
    if len(found) != 1:
        return []
    d, out = found[0], []
    media = list(g.objects(d, DCAT.mediaType))
    if not media:
        out.append(f"{name}: no media type")
    for m in media:
        if not (isinstance(m, URIRef) and str(m).startswith(IANA)):
            kind = "text" if isinstance(m, Literal) else "a link outside IANA"
            out.append(f"{name}: media type '{show(m)}' is {kind}, it should be a link that starts with {IANA}")
    if not list(g.objects(d, DCT["format"])):
        if list(g.objects(d, DCAT["format"])):
            out.append(f"{name}: the file format is written with dcat:format, the DCAT standard uses dcterms:format")
        else:
            out.append(f"{name}: no file format")
    return out


def stated_size(g):
    """the dcat:byteSize an FDP distribution states (None when it states none)"""
    for d in g.subjects(RDF.type, DCAT.Distribution):
        for v in g.objects(d, DCAT.byteSize):
            try:
                return int(v)
            except ValueError:
                return -1
    return None


def rules_cover_distributions():
    try:
        text = open(RULE_TESTS, encoding="utf-8").read()
    except FileNotFoundError:
        return [f"{RULE_TESTS} not found"]
    return [f"no test for {p} in {RULE_TESTS}" for p in ("distribution/original-csv", "distribution/ttl")
            if f"path: {p}" not in text]


def check_fdp(gr):
    if "fdp_dataset" in gr:
        issues = dataset_issues(gr["fdp_dataset"])
        labels = {"F1": "F1. dataset record: title, description, licence, publisher, keywords, landing page, theme, language",
                  "F2": "F2. dataset record: every contact point is a mailto: link",
                  "F3": f"F3. dataset record: identifier is {DATASET_ID}"}
        for key, label in labels.items():
            report(not issues[key], label, "; ".join(issues[key][:3]))
        if not list(gr["fdp_dataset"].objects(None, DCT.source)):
            warn("dataset record: no source (dcterms:source, the Kaggle link). The FDP schema needs a field for it")
    else:
        skip("F1 to F3 (dataset record)", "the file did not parse, see A")

    for key, expected, name, label in (("fdp_csv", CSV_ID, "original CSV", "F4"), ("fdp_ttl", TTL_ID, "RDF", "F5")):
        if key not in gr:
            skip(f"{label} ({name} distribution)", "the file did not parse, see A")
            continue
        issues = distribution_issues(gr[key], expected)
        report(not issues, f"{label}. {name} distribution: title, licence, identifier, download and access URL are {expected}",
               "; ".join(issues[:3]))
        for w in distribution_warnings(gr[key], f"{name} distribution"):
            warn(w)

    problems = rules_cover_distributions()
    report(not problems, "F6. the redirect rules test both distribution links", "; ".join(problems))

    if "fdp_ttl" in gr:
        actual = os.path.getsize(FILES["data"]) if os.path.exists(FILES["data"]) else None
        stated = stated_size(gr["fdp_ttl"])
        if stated is None:
            warn(f"RDF distribution: no byte size stated (data/rdf/library.ttl has {actual} bytes)")
        else:
            report(stated == actual, "F7. the byte size stated for the RDF distribution equals the real file size",
                   f"record says {stated}, file has {actual}")


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

# A small model of what the FAIR Data Point exports: record IRIs on localhost, the W3ID link kept
# in a sub-record, contact points as mailto: links.
FDP_PREFIXES = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix fdpo: <https://w3id.org/fdp/fdp-o#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

GOOD_FDP_DATASET = FDP_PREFIXES + f"""
<http://localhost:8080/dataset/x> a dcat:Dataset ;
  dcterms:title "Library Catalogue" ; dcterms:description "A catalogue." ;
  dcterms:license <https://spdx.org/licenses/MIT> ;
  dcterms:publisher [ a foaf:Agent ; foaf:name "Group 23" ] ;
  dcterms:language <http://id.loc.gov/vocabulary/iso639-1/en> ;
  dcat:keyword "library" ; dcat:landingPage <https://github.com/x/y> ;
  dcat:theme <http://publications.europa.eu/resource/authority/data-theme/EDUC> ;
  dcat:contactPoint <mailto:a@student.utwente.nl> , <mailto:b@student.utwente.nl> ;
  fdpo:metadataIdentifier <http://localhost:8080/dataset/x#identifier> .
<http://localhost:8080/dataset/x#identifier> dcterms:identifier "{DATASET_ID}" .
"""


def good_fdp_distribution(link):
    return FDP_PREFIXES + f"""
<http://localhost:8080/distribution/y> a dcat:Distribution ;
  dcterms:title "A file" ; dcterms:license <https://spdx.org/licenses/MIT> ;
  dcat:accessURL <{link}> ; dcat:downloadURL <{link}> ;
  dcat:mediaType <{IANA}text/csv> ; dcterms:format <http://publications.europa.eu/resource/authority/file-type/CSV> ;
  fdpo:metadataIdentifier <http://localhost:8080/distribution/y#identifier> .
<http://localhost:8080/distribution/y#identifier> dcterms:identifier "{link}" .
"""


def selftest(gr):
    print("\nSelf-test: each broken record below MUST be rejected")

    def book_case(label, old, new):
        assert old in GOOD_BOOK, old
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

    fixture_text = open(FILES["fixture"], encoding="utf-8").read()
    shapes = gr["dataset_shape"] + gr["distribution_shape"]

    def meta_case(label, old, new, count=1):
        assert old in fixture_text, old
        g = Graph().parse(data=fixture_text.replace(old, new, count), format="turtle")
        ok, _ = shacl(g, shapes)
        report(not ok, f"E. shapes reject: {label}")

    meta_case("dataset without licence", "    dcterms:license <https://spdx.org/licenses/MIT> ;\n    dcterms:publisher", "    dcterms:publisher")
    meta_case("dataset without keywords", '    dcat:keyword "library" , "catalogue" , "books" , "FAIR" , "Schema.org" ;\n', "")
    meta_case("distribution without media type",
              "    dcat:mediaType <https://www.iana.org/assignments/media-types/text/csv> ;\n", "", 1)
    meta_case("distribution without download URL",
              "    dcat:downloadURL <https://w3id.org/FAIR-course-UT/2026/group23/distribution/original-csv> ;\n", "")
    meta_case("media type as plain text", "dcat:mediaType <https://www.iana.org/assignments/media-types/text/turtle>",
              'dcat:mediaType "text/turtle"')

    ghost = Graph().parse(data=GOOD_BOOK, format="turtle")
    ghost.add((DATA["author-ghost"], RDF.type, SCHEMA.Person))
    report(bool(orphan_authors(ghost)), "E. data rejected: author node without a book")

    # the checks for the FAIR Data Point records
    def fdp(text):
        return Graph().parse(data=text, format="turtle")

    def dataset_case(label, old, new):
        assert old in GOOD_FDP_DATASET, old
        found = dataset_issues(fdp(GOOD_FDP_DATASET.replace(old, new)))
        report(any(found.values()), f"E. FDP check rejects: {label}")

    def distribution_case(label, text, expected, extra=None):
        report(bool(distribution_issues(fdp(text), expected)), f"E. FDP check rejects: {label}")

    report(not any(dataset_issues(fdp(GOOD_FDP_DATASET)).values()), "E. a correct FDP dataset record is accepted")
    report(not distribution_issues(fdp(good_fdp_distribution(CSV_ID)), CSV_ID), "E. a correct FDP distribution record is accepted")
    dataset_case("contact point without mailto:", "<mailto:b@student.utwente.nl>", "<b@student.utwente.nl>")
    dataset_case("identifier that holds a long text instead of one link", f'"{DATASET_ID}"',
                 f'"""{DATASET_ID}\n@prefix dcat: <http://www.w3.org/ns/dcat#> .\nmore text"""')
    dataset_case("dataset without licence", "  dcterms:license <https://spdx.org/licenses/MIT> ;\n", "")
    good_csv = good_fdp_distribution(CSV_ID)
    distribution_case("download link that is not the W3ID link", good_csv.replace(f"dcat:downloadURL <{CSV_ID}>", "dcat:downloadURL <http://localhost:8080/file>"), CSV_ID)
    distribution_case("distribution that carries the other distribution's identifier", good_fdp_distribution(TTL_ID), CSV_ID)
    wrong = Graph().parse(data=good_fdp_distribution(TTL_ID) + '\n<http://localhost:8080/distribution/y> dcat:byteSize "1"^^xsd:nonNegativeInteger .\n', format="turtle")
    report(stated_size(wrong) != os.path.getsize(FILES["data"]), "E. FDP check rejects: wrong byte size")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    gr = check_syntax()
    core_ok = all(k in gr for k in CORE)
    if core_ok:
        check_records(gr)
        check_uris(gr)
        check_shapes(gr)
    else:
        report(False, "B to D need the ontology, the data, the shapes and the example record to parse")
    check_fdp(gr)
    if args.selftest and core_ok:
        selftest(gr)

    print()
    if warnings:
        print(f"{len(warnings)} warning(s). They are not failures: they list what the FAIR Data Point schemas still need.")
    if failures:
        print(f"{len(failures)} check(s) FAILED:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
