#!/usr/bin/env python3
"""
draw_ontology.py  -  draw the library ontology as a class diagram (PNG + SVG).

The classes, the subclass links, the "disjoint with" link and the lib: properties are READ from
ontology/library-ontology.ttl, so the picture cannot drift away from the file. The Schema.org
properties that the RDF data uses but the ontology file only mentions in a comment (author, genre,
aggregateRating, name, datePublished, inLanguage, keywords) are listed in REUSED below; they are the
same ones build_rdf.py writes.

Needs Graphviz (the `dot` program) and rdflib.

Usage (from the repo root):
  python scripts/draw_ontology.py ontology/library-ontology.ttl documentation/ontology-diagram
  -> writes documentation/ontology-diagram.png and documentation/ontology-diagram.svg
"""
import html
import subprocess
import sys

from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.namespace import XSD

LIB = Namespace("https://w3id.org/FAIR-course-UT/2026/group23/ont#")

# (label shown in the box, datatype) for properties reused from Schema.org on LibraryBook
REUSED_LITERALS = [
    ("schema:name", "xsd:string"),
    ("schema:datePublished", "xsd:gYear"),
    ("schema:inLanguage", "xsd:string"),
    ("schema:keywords", "xsd:string"),
]

OURS_FILL, OURS_LINE = "#DCEBFA", "#1F5FA8"
EXT_FILL, EXT_LINE = "#F1F1F1", "#6B6B6B"
TEXT = "#1A1A1A"


def short(g, term):
    """prefix:Local form, e.g. lib:LibraryBook"""
    s = g.namespace_manager.normalizeUri(term)
    return s.strip("<>")


def esc(s):
    return html.escape(str(s), quote=True)


def lab(text, color):
    """HTML edge label on a white background, so the line does not cross the words"""
    return (f'<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="2" BGCOLOR="white">'
            f'<TR><TD><FONT COLOR="{color}" POINT-SIZE="10">{esc(text)}</FONT></TD></TR></TABLE>>')


def class_node(name, ours, rows=None):
    fill, line = (OURS_FILL, OURS_LINE) if ours else (EXT_FILL, EXT_LINE)
    out = [f'<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5" COLOR="{line}" BGCOLOR="{fill}">',
           f'<TR><TD ALIGN="CENTER"><B>{esc(name)}</B></TD></TR>']
    for title, items in rows or []:
        out.append(f'<HR/><TR><TD ALIGN="LEFT"><FONT POINT-SIZE="9" COLOR="#555555"><I>{esc(title)}</I></FONT></TD></TR>')
        for left, right in items:
            out.append(f'<TR><TD ALIGN="LEFT"><FONT POINT-SIZE="10">{esc(left)} : {esc(right)}</FONT></TD></TR>')
    out.append("</TABLE>")
    return "".join(out)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    ttl, stem = sys.argv[1], sys.argv[2]
    g = Graph().parse(ttl, format="turtle")

    # classes and datatype properties declared by us
    our_classes = sorted(c for c in g.subjects(RDF.type, OWL.Class) if str(c).startswith(str(LIB)))
    dt_props = sorted(p for p in g.subjects(RDF.type, OWL.DatatypeProperty) if str(p).startswith(str(LIB)))
    obj_props = sorted(p for p in g.subjects(RDF.type, OWL.ObjectProperty) if str(p).startswith(str(LIB)))

    def xsd_name(rng):
        return "xsd:" + str(rng).split("#")[-1] if str(rng).startswith(str(XSD)) else short(g, rng)

    own_rows = [(short(g, p), xsd_name(g.value(p, RDFS.range))) for p in dt_props]
    reused_rows = list(REUSED_LITERALS)

    L = []
    L.append("digraph ontology {")
    L.append('  rankdir=BT; nodesep=0.6; ranksep=0.9; bgcolor="white"; pad=0.3; splines=true;')
    L.append(f'  node [shape=plain, fontname="Helvetica", fontcolor="{TEXT}"];')
    L.append(f'  edge [fontname="Helvetica", fontsize=10, fontcolor="{TEXT}", color="{TEXT}"];')

    # the book class is drawn as a UML box with its attributes
    for c in our_classes:
        n = short(g, c)
        if n == "lib:LibraryBook":
            rows = [("added by us, declared in the ontology", own_rows),
                    ("reused from Schema.org", reused_rows)]
            L.append(f'  "{n}" [label=<{class_node(n, True, rows)}>];')
        else:
            L.append(f'  "{n}" [label=<{class_node(n, True)}>];')

    # external classes: parents we build on, plus the Schema.org classes the data points to
    parents = {short(g, o) for c in our_classes for o in g.objects(c, RDFS.subClassOf)}
    for n in sorted(parents):
        L.append(f'  "{n}" [label=<{class_node(n, False)}>];')
    L.append(f'  "authors" [label=<{class_node("schema:Person or schema:Organization", False)}>];')
    L.append(f'  "rating" [label=<{class_node("schema:AggregateRating", False)}>];')

    # subclass links (hollow triangle, as in UML)
    for c in our_classes:
        for o in g.objects(c, RDFS.subClassOf):
            L.append(f'  "{short(g, c)}" -> "{short(g, o)}" [arrowhead=empty, label={lab("subClassOf", OURS_LINE)}, color="{OURS_LINE}"];')

    # disjointWith (no arrow, red dashed)
    for a, b in g.subject_objects(OWL.disjointWith):
        L.append(f'  "{short(g, a)}" -> "{short(g, b)}" [dir=none, style=dashed, color="#B3261E", label={lab("disjointWith", "#B3261E")}, constraint=false];')

    # our object properties (solid blue)
    for p in obj_props:
        d, r = g.value(p, RDFS.domain), g.value(p, RDFS.range)
        L.append(f'  "{short(g, d)}" -> "{short(g, r)}" [label={lab(short(g, p), OURS_LINE)}, color="{OURS_LINE}", penwidth=1.6];')

    # Schema.org properties used in the data (dashed grey)
    L.append(f'  "lib:LibraryBook" -> "authors" [label={lab("schema:author", EXT_LINE)}, style=dashed, color="{EXT_LINE}"];')
    L.append(f'  "lib:LibraryBook" -> "lib:Genre" [label={lab("schema:genre", EXT_LINE)}, style=dashed, color="{EXT_LINE}"];')
    L.append(f'  "lib:LibraryBook" -> "rating" [label={lab("schema:aggregateRating", EXT_LINE)}, style=dashed, color="{EXT_LINE}"];')

    legend = (
        '<TABLE BORDER="0" CELLSPACING="0" CELLPADDING="3">'
        f'<TR><TD ALIGN="LEFT"><FONT COLOR="{OURS_LINE}"><B>Blue</B></FONT> boxes and solid arrows: defined by us (prefix lib:)</TD></TR>'
        f'<TR><TD ALIGN="LEFT"><FONT COLOR="{EXT_LINE}"><B>Grey</B></FONT> boxes and dashed arrows: reused from Schema.org or SKOS</TD></TR>'
        '<TR><TD ALIGN="LEFT">Hollow triangle: subClassOf. Red dashed line: disjointWith (a thing cannot be both).</TD></TR>'
        '</TABLE>'
    )
    L.append(f'  label=<{legend}>; labelloc=b; labeljust=l; fontname="Helvetica"; fontsize=10;')
    L.append("}")
    dot_src = "\n".join(L)

    with open(stem + ".dot", "w", encoding="utf-8") as f:
        f.write(dot_src)
    for fmt, extra in (("png", ["-Gdpi=200"]), ("svg", [])):
        subprocess.run(["dot", f"-T{fmt}", *extra, stem + ".dot", "-o", f"{stem}.{fmt}"], check=True)
    print(f"wrote {stem}.png, {stem}.svg, {stem}.dot")


if __name__ == "__main__":
    main()
