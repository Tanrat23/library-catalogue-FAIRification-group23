# Ontology, mapping decisions and RDF examples

Library Catalogue FAIRification, FAIR Data Engineering 2026-1A, University of Twente.
Authors: Prutha Vijaykumar Thakkar and Rattan Kumar. Version 0.1.0, 23 October 2026.
This document covers the semantic model and RDF part of the project (Person 2).

## 1. At a glance

- Source data: Kaggle "Library Catalog" (MIT licence), cleaned with OpenRefine and then repaired by `scripts/patch_csv.py`.
- Result: **2077 books**, described in **37,172 RDF triples** (`data/rdf/library.ttl`, Turtle).
- Vocabulary: Schema.org first, plus a small library ontology (`ontology/library-ontology.ttl`) with 3 classes and 5 properties.
- Quality gate: SHACL shapes and 7 URI checks, all passing (see section 7).
- Namespaces:

| prefix | namespace | what lives there |
|---|---|---|
| `lib:` | `https://w3id.org/FAIR-course-UT/2026/group23/ont#` | our own classes and properties |
| `data:` | `https://w3id.org/FAIR-course-UT/2026/group23/data#` | books, authors, genres, sections |
| `schema:` | `https://schema.org/` | reused Schema.org terms |
| `skos:` | `http://www.w3.org/2004/02/skos/core#` | concepts and concept schemes |
| `xsd:` | `http://www.w3.org/2001/XMLSchema#` | datatypes |

## 2. The model in one picture

![Class diagram of the library ontology](ontology-diagram.png)

- One `schema:Book` (also typed `lib:LibraryBook`) per CSV row.
- A book points to its author (a shared `schema:Person` or `schema:Organization`), its genre (a `lib:Genre`) and its section (a `lib:Section`).
- Genres and sections are SKOS concepts in two concept schemes, so each label exists once and can be corrected in one place.
- Ratings sit in a small `schema:AggregateRating` node on the book.
- Blue means defined by us, grey means reused from Schema.org or SKOS. The diagram is generated from the ontology file by `scripts/draw_ontology.py`.

The ontology was also loaded into WebProtégé to check that identifiers, labels, comments, parents, domains and ranges read back correctly:

![WebProtégé class Library book](webprotege-class-library-book.png)

![WebProtégé property price](webprotege-price-property.png)

![WebProtégé property in section](webprotege-in-section-property.png)

## 3. Ontology reference

Generated from `ontology/library-ontology.ttl`. Licence: CC BY 4.0. Identifier: `https://w3id.org/FAIR-course-UT/2026/group23/ont`.

### Classes

| term | label | subclass of | disjoint with | meaning |
|---|---|---|---|---|
| `lib:Genre` | Genre | `skos:Concept` |  | A literary genre label from the catalogue, for example Drama or Poetry. Modelled as a SKOS concept so spelling variants become visible and fixable in one place. |
| `lib:LibraryBook` | Library book | `schema:Book` |  | A book as recorded in this library's catalogue. One row of the cleaned catalogue CSV is one LibraryBook. |
| `lib:Section` | Section | `skos:Concept` | `lib:Genre` | An area of the library where books are shelved, for example Fiction or Children. Modelled as a SKOS concept so sections can be listed and reused. |

### Properties

| term | kind | domain | range | functional | meaning |
|---|---|---|---|---|---|
| `lib:cataloguePosition` | data | `lib:LibraryBook` | `xsd:string` | yes | The unique shelf-style code of a book in the catalogue, for example A1-B1-0001. This is the identifier we build every book URI from. |
| `lib:price` | data | `lib:LibraryBook` | `xsd:decimal` | yes | Price of the book as recorded in the source catalogue. The source does not state a currency, so none is asserted. |
| `lib:recordedIsbn` | data | `lib:LibraryBook` | `xsd:string` | yes | The ISBN text exactly as found in the source. The values have 12 digits, so they are not valid ISBN-13 numbers and must not be used for linking. |
| `lib:timesBorrowed` | data | `lib:LibraryBook` | `xsd:nonNegativeInteger` | yes | How many times the book has been borrowed, as recorded in the source catalogue. |
| `lib:inSection` | object | `lib:LibraryBook` | `lib:Section` | yes | Links a book to the library section where it is shelved. |

- "Functional" means a book has at most one value, so two prices for one book would be an error.
- Everything else (title, author, year, genre, language, keywords, rating) is reused from Schema.org and is not redefined.

## 4. Mapping: CSV column to RDF

"Filled" counts the rows where the cell is not blank. A blank cell produces no triple.

| CSV column | example | RDF | datatype or target | filled |
|---|---|---|---|---|
| `catalogue_position` | A1-B1-0001 | book IRI `data:book-A1-B1-0001` and `lib:cataloguePosition` | IRI and `xsd:string` | 2077 of 2077 |
| `title` | Enormous Room | `schema:name` | `xsd:string` | 2077 of 2077 |
| `author` | E. E. Cummings | `schema:author` | shared `schema:Person` or `schema:Organization` with `schema:name` | 2076 books linked (2077 cells, 1 is "Anonymous") |
| `year_published` | 1949 | `schema:datePublished` | `xsd:gYear` | 2072 of 2077 |
| `genre` | Drama | `schema:genre` | `lib:Genre` concept with `skos:prefLabel` | 2026 of 2077 |
| `section` | Fiction | `lib:inSection` | `lib:Section` concept with `skos:prefLabel` | 2019 of 2077 |
| `times_borrowed` | 3 | `lib:timesBorrowed` | `xsd:nonNegativeInteger` | 2071 of 2077 |
| `ratings` and `ratings_count` | 4.14 and 2 | `schema:aggregateRating` | node with `ratingValue`, `ratingCount`, `bestRating 5`, `worstRating 1` | 1759 of 2077 (count present for 1735) |
| `price` | 14.66 | `lib:price` | `xsd:decimal`, no currency | 1882 of 2077 |
| `language` | en | `schema:inLanguage` | `xsd:string` | 2075 of 2077 |
| `isbn` | 978-5-720-1389-0 | `lib:recordedIsbn` | `xsd:string` | 177 of 2077 |
| `subjects` | Fiction, war and military, ... | `schema:keywords` | one `xsd:string`, kept whole | 2027 of 2077 |

## 5. Mapping decisions and reasons

| # | decision | reason | FAIR |
|---|---|---|---|
| 1 | Reuse Schema.org for everything it covers, add `lib:` terms only where Schema.org has no fit (3 classes and 5 properties: position, loans, price, recorded ISBN, section) | Other tools already understand Schema.org, and fewer new terms means less to maintain | I1, I2 |
| 2 | Book IRI is `data#book-<catalogue position>` | The position is unique (2077 of 2077), stable and meaningful to the library | F1 |
| 3 | Hash IRIs (`data#...`) under the course prefix `https://w3id.org/FAIR-course-UT/2026/group23/` | The course sets the prefix: `.../ont` for the ontology and `.../data#` for the data, served through the course's W3ID relay. The part after `#` is never sent to a server, so one redirect for `/data` serves every record | F1, A1 |
| 4 | Authors, genres and sections are their own resources | One place to fix a spelling, one node linking many books, and a target for links to other datasets | I3 |
| 5 | Person or Organization is decided by name patterns and a short list of known organisations | The CSV has no type column. Result: 839 persons and 35 organisations (41 books have an organisation author) | limitation, see section 9 |
| 6 | "Anonymous" gets no author triple (1 book) | Avoids inventing a person called Anonymous | accuracy |
| 7 | " & " in an author cell creates two authors (1 book: A4-B4-0008) | Each person gets a node of their own | I3 |
| 8 | Years are `xsd:gYear`. Years later than 2026 are blanked by the patch step | Two impossible values were left by the OpenRefine step: A2-B3-0024 (2999) and A4-B3-0082 (2119) | R1 |
| 9 | A blank cell means no triple, never an empty string or a made-up value | Missing data stays visibly missing, and the table above shows how complete each property is | R1 |
| 10 | `isbn` is published as `lib:recordedIsbn`, not `schema:isbn` | All 177 values have 12 digits (for example 978-5-720-1389-0) and an ISBN-13 needs 13, so `schema:isbn` would claim a validity we cannot support | R1 |
| 11 | `lib:price` has no currency | The source does not state one | R1 |
| 12 | Rating scale is assumed to be 1 to 5 | Observed values range from 1.03 to 5.0, but the source does not state the scale | R1 |
| 13 | `subjects` stays one `schema:keywords` string | The separator (a comma) also occurs inside headings such as "Fiction, historical", so splitting would break terms | R1 |
| 14 | Genre and Section are separate classes declared disjoint | A shelf area and a literary genre are different things, and a reasoner can flag any mix-up | I1 |
| 15 | Triples are generated by a script, not by the OpenRefine RDF extension | One command reproduces the file exactly, it is version controlled and it is tested | R1.2 |
| 16 | Text repairs (broken accents) are logged cell by cell in `data/patch_log.csv` | Anyone can see what changed from the OpenRefine export: 771 subjects, 11 titles, 10 authors, 2 years | R1.2 |
| 17 | Licences: data MIT (as the source), ontology CC BY 4.0 | Proposed default, to be confirmed by both authors before publishing | R1.1 |
| 18 | The metadata has two distributions: the original CSV and the FAIRified RDF | The course asks for these two. The cleaned CSV stays in the repository as the input of the pipeline | F2, R1.2 |

## 6. RDF examples (real excerpts from `data/rdf/library.ttl`)

### 6.1 A complete book with its shared genre and section

```turtle
@prefix data: <https://w3id.org/FAIR-course-UT/2026/group23/data#> .
@prefix lib: <https://w3id.org/FAIR-course-UT/2026/group23/ont#> .
@prefix schema: <https://schema.org/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

data:book-A1-B1-0001 a schema:Book,
        lib:LibraryBook ;
    schema:aggregateRating [ a schema:AggregateRating ;
            schema:bestRating 5 ;
            schema:ratingCount 2 ;
            schema:ratingValue 4.14 ;
            schema:worstRating 1 ] ;
    schema:author data:author-e-e-cummings ;
    schema:datePublished "1949"^^xsd:gYear ;
    schema:genre data:genre-drama ;
    schema:inLanguage "en" ;
    schema:keywords "Fiction, biographical, American fiction (fictional works by one author), Fiction, war & ..." ;
    schema:name "Enormous Room" ;
    lib:cataloguePosition "A1-B1-0001" ;
    lib:inSection data:section-fiction ;
    lib:price 14.66 ;
    lib:timesBorrowed "3"^^xsd:nonNegativeInteger .

data:author-e-e-cummings a schema:Person ;
    schema:name "E. E. Cummings" .

data:genre-drama a lib:Genre ;
    skos:inScheme data:scheme-genres ;
    skos:prefLabel "Drama"@en .

data:section-fiction a lib:Section ;
    skos:inScheme data:scheme-sections ;
    skos:prefLabel "Fiction"@en .
```

- The book, its genre and its section are three separate resources joined by IRIs.
- The rating is a blank node (it has no IRI of its own) because nobody needs to link to it.

### 6.2 A book whose author is an organisation

```turtle
data:book-A2-B2-0063 a schema:Book,
        lib:LibraryBook ;
    schema:author data:author-early-english-text-society ;
    schema:datePublished "1864"^^xsd:gYear ;
    schema:inLanguage "en" ;
    schema:name "[Publications]. Original series" ;
    lib:cataloguePosition "A2-B2-0063" ;
    lib:price 9.99 ;
    lib:timesBorrowed "1"^^xsd:nonNegativeInteger .

data:author-early-english-text-society a schema:Organization ;
    schema:name "Early English Text Society" .
```

- No genre, section, rating or keywords triples exist here because those cells were blank.

### 6.3 A book with two authors and a rating

```turtle
data:book-A4-B4-0008 a schema:Book,
        lib:LibraryBook ;
    schema:aggregateRating [ a schema:AggregateRating ;
            schema:bestRating 5 ;
            schema:ratingCount 1 ;
            schema:ratingValue 4.19 ;
            schema:worstRating 1 ] ;
    schema:author data:author-amanda-hendrix,
        data:author-charles-wohlforth ;
    schema:datePublished "2016"^^xsd:gYear ;
    schema:genre data:genre-science ;
    schema:inLanguage "en" ;
    schema:keywords "Manned space flight, Astronautics, Space flight, physiological effect" ;
    schema:name "Beyond Earth" ;
    lib:cataloguePosition "A4-B4-0008" ;
    lib:inSection data:section-science ;
    lib:price 14.84 ;
    lib:timesBorrowed "2"^^xsd:nonNegativeInteger .

data:author-amanda-hendrix a schema:Person ;
    schema:name "Amanda Hendrix" .

data:author-charles-wohlforth a schema:Person ;
    schema:name "Charles Wohlforth" .
```

### 6.4 Queries that the model makes possible

Five authors with the most books:

```sparql
SELECT ?name (COUNT(?book) AS ?books) WHERE {
  ?book a lib:LibraryBook ; schema:author ?author .
  ?author schema:name ?name .
} GROUP BY ?name ORDER BY DESC(?books) ?name LIMIT 5
```

| author | books |
|---|---|
| Agatha Christie | 65 |
| William Shakespeare | 41 |
| Charles Dickens | 36 |
| Arthur Conan Doyle | 31 |
| John Buchan | 27 |

Average times borrowed per section:

```sparql
SELECT ?section (AVG(?loans) AS ?average_loans) WHERE {
  ?book lib:inSection ?s ; lib:timesBorrowed ?loans .
  ?s skos:prefLabel ?section .
} GROUP BY ?section ORDER BY DESC(?average_loans)
```

| section | average times borrowed |
|---|---|
| Young Adult | 203.5 |
| Non-Fiction | 100.9 |
| Fiction | 42.4 |
| Science | 35.4 |
| Children | 26.4 |
| Reference | 13.8 |
| History | 13.4 |
| Humanities | 3.9 |
| Rare Books | 0.0 |

## 7. Validation

Command: `python scripts/validate.py --selftest | tee documentation/validation_log.txt`. Run on 23 October 2026. Result: **All checks passed** (16 checks and 13 self-tests). The full output is saved in `documentation/validation_log.txt`.

| check | what it proves |
|---|---|
| A | The ontology, the data, the three shapes and the metadata record all parse as Turtle |
| B | Every book conforms to `shapes/book-shape.ttl` (one title, a position like A1-B1-0001, a year from 1000 to 2026, a non-negative price, a lowercase language code, authors that are resources, rating between 1 and 5) |
| C1 | Every subject IRI is in the `data#` namespace |
| C2 | No illegal characters in any IRI |
| C3 | No dangling references: every author, genre and section that is used is also described |
| C4 | Every `lib:` term used in the data is declared in the ontology |
| C5 | Catalogue positions are unique (2077 values) |
| C6 | Each book IRI is built from its own catalogue position |
| C7 | The number of books equals the number of CSV rows (2077 and 2077) |
| D | `metadata/dataset-record.ttl` conforms to the Dataset and Distribution shapes |
| D2 | The byte size stated in the metadata equals the real size of `data/rdf/library.ttl` |
| E | 13 self-tests: broken records (year 2999, negative price, missing title, capital-letter language, plain-text author, bad position, dataset without licence or keywords, distribution without media type or download URL, media type as text, wrong byte size) must be rejected, and one correct book must be accepted |

- The self-tests matter because a checker that never fails proves nothing: they show the checks can reject bad data.
- The ontology was viewed in WebProtégé but no reasoner was run on it.

## 8. Reproduce everything

From the repository root:

```
pip install -r requirements.txt
python scripts/patch_csv.py data/library_catalogue_clean.csv data/library_catalogue_repaired.csv data/patch_log.csv
python scripts/build_rdf.py data/library_catalogue_repaired.csv data/rdf/library.ttl --base https://w3id.org/FAIR-course-UT/2026/group23/
python scripts/validate.py --selftest | tee documentation/validation_log.txt
python scripts/check_w3id_rules.py w3id/rules/FAIR-course-UT/2026/group23 --repo-root .
python scripts/draw_ontology.py ontology/library-ontology.ttl documentation/ontology-diagram
```

- The last command needs Graphviz (the `dot` program).
- Tested with Python 3.13, rdflib 7.6.0, pySHACL 0.40.1 and ftfy 6.3.1. `requirements.txt` asks for rdflib 7.0, pyshacl 0.26 and ftfy 6.1 or newer.
- The input is Person 1's OpenRefine export `data/library_catalogue_clean.csv`. Re-running the commands gives byte-identical output.

## 9. Known limitations and open items

- **W3ID rules not merged yet.** The `https://w3id.org/FAIR-course-UT/2026/group23/...` addresses resolve only after the files are public on GitHub and our pull request to the course relay (`luizbonino/pid-relay`) has passed its checks. The rules and their tests are in `w3id/rules/FAIR-course-UT/2026/group23/`, and `scripts/check_w3id_rules.py` checks them locally.
- **Organisation detection is rule-based.** The 35 organisations the script printed should be reviewed by eye. A wrong guess changes only the type (`schema:Person` or `schema:Organization`) of one author node.
- **ISBN values are not usable for linking.** They have 12 digits, so they are kept as text only.
- **Prices:** 24 values are above 1000, 12 of them first editions in the Rare Books section (A7-B4). They are kept as in the source, and no currency is known.
- **Rating scale** is assumed, see decision 12.
- **Open Library links** are not yet generated: `scripts/link_openlibrary.py` is written and tested on sample responses but has not yet been run against the live service.
- **Contact points** in `metadata/dataset-record.ttl` are the two authors' university addresses.

## 10. Related files

| path | purpose |
|---|---|
| `ontology/library-ontology.ttl` | the ontology (master copy) |
| `data/library_catalogue_original.csv` | the original Kaggle file (first distribution; Person 1) |
| `data/library_catalogue_clean.csv` | Person 1's OpenRefine export (input of the pipeline) |
| `data/library_catalogue_repaired.csv` | the export after the text repairs of `scripts/patch_csv.py` |
| `data/patch_log.csv` | every cell changed by the patch step |
| `data/rdf/library.ttl` | the catalogue as RDF |
| `shapes/book-shape.ttl`, `shapes/dataset-shape.ttl`, `shapes/distribution-shape.ttl` | SHACL shapes |
| `metadata/dataset-record.ttl` | example FAIR Data Point records |
| `scripts/` | patch, build, validate, link and draw scripts |
| `w3id/rules/FAIR-course-UT/2026/group23/` and `w3id/README.md` | redirect rules and tests for the persistent identifiers, and the steps to submit them |
