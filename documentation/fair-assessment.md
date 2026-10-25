# FAIR Assessment: Library Catalogue Dataset

Library Catalogue FAIRification, FAIR Data Engineering 2026-1A, University of Twente, Group 23.
Authors: Prutha Vijaykumar Thakkar and Rattan Kumar. Version 0.1, 25 October 2026.

This is a self assessment. Every piece of evidence is a file or a command in this repository, so each statement can be checked.

## 1. Before and after

### 1.1 Findable (F)

* **Before:** The original dataset was discoverable only through Kaggle's internal search ecosystem. It lacked a globally unique, persistent identifier (PID) and relied on basic platform-specific metadata.
* **After:** The dataset and its distributions are now assigned globally unique and persistent W3ID identifiers (e.g., `https://w3id.org/FAIR-course-UT/2026/group23/dataset`). Rich, machine-readable metadata is recorded in a FAIR Data Point and exported to `metadata/`. The FAIR Data Point runs locally, so the records cannot yet be found by others (see F4 below).

### 1.2 Accessible (A)

* **Before:** Accessing the original CSV required navigating a proprietary platform and potentially logging into a user account.
* **After:** The dataset, its two distributions, the ontology and the shapes are retrievable by their W3ID identifiers using standard, open HTTP protocols. The W3ID relay automatically resolves to publicly accessible raw download links hosted on GitHub. The metadata records are files in the public repository.

### 1.3 Interoperable (I)

* **Before:** The data was provided as a flat CSV file relying entirely on plain text strings. It lacked formal, accessible, shared, and broadly applicable semantic vocabularies.
* **After:** The cleaned dataset is transformed into an RDF Linked Data format (Turtle). It utilizes established semantic web vocabularies (such as Schema.org) and a custom domain ontology to explicitly define relationships between books, authors, genres, and library sections.

### 1.4 Reusable (R)

* **Before:** The dataset contained incomplete records (such as missing titles) and had no detailed, machine-readable provenance. The MIT licence was stated only on the Kaggle page.
* **After:** The data has been cleaned to remove unusable records. The transformations are recorded in `cleaning-methodology.md` and `openrefine-operations.json`, and the text repairs are logged in `data/patch_log.csv`. The metadata records now state the data provenance (`dcterms:source`) and the usage licence (`dcterms:license`), and they use community standards (Schema.org, DCAT, SHACL).

## 2. Summary

- **Met:** 10 of 13 principles.
- **Partial:** 3 of 13 (F4, A2, R1.1).
- **Open:** none.
- **Validation state:** `scripts/validate.py --selftest` ends with "All checks passed." It shows 46 PASS lines and 1 WARN (the RDF distribution record states no byte size). See `documentation/validation_log.txt`.

| ID | principle | status | main evidence |
|---|---|---|---|
| F1 | Globally unique and persistent identifiers | Met | W3ID namespace `https://w3id.org/FAIR-course-UT/2026/group23/`, 9 merged rules |
| F2 | Rich metadata | Met | DCAT records in `metadata/` |
| F3 | Metadata include the identifier of the data | Met | W3ID links in the download and access URLs |
| F4 | Registered or indexed in a searchable resource | Partial | FAIR Data Point runs on a local machine only |
| A1 | Retrievable by identifier with a standard protocol | Met | All 9 W3ID addresses end with HTTP 200 over HTTPS |
| A2 | Metadata stay available when the data are gone | Partial | Records are in the public repository, no long-term archive |
| I1 | Formal, shared language | Met | RDF in Turtle, DCAT, SHACL |
| I2 | FAIR vocabularies | Met | Schema.org, SKOS, DCAT, own `lib:` ontology |
| I3 | Qualified references to other data | Met | 92.1% of books linked to Open Library |
| R1 | Richly described, accurate attributes | Met | 13 documented fields, SHACL book shape |
| R1.1 | Clear usage licence | Partial | MIT stated for the data, no `LICENSE` file, other licences open |
| R1.2 | Detailed provenance | Met | Original kept, OpenRefine history, repair log, scripts |
| R1.3 | Community standards | Met | Schema.org, DCAT, FAIR Data Point 1.18.0, SHACL |

## 3. Findable

### F1 Globally unique and persistent identifiers (Met)

- Every identifier lives under `https://w3id.org/FAIR-course-UT/2026/group23/`:
    - ontology: `.../ont` (terms are `.../ont#Term`)
    - data: `.../data` (records are `.../data#book-<catalogue_position>`, for example `.../data#book-A1-B1-0001`)
    - dataset: `.../dataset`
    - distributions: `.../distribution/original-csv` and `.../distribution/ttl`
    - shapes: `.../shapes/dataset`, `.../shapes/distribution`, `.../shapes/book`
- The 2,077 book IRIs are unique because each is built from the unique `catalogue_position` (checks C5 and C6 pass).
- The 9 redirect rules were merged into the course relay on 23 October 2026 (pull request 33 to `luizbonino/pid-relay`). The rules and their tests are in `w3id/rules/FAIR-course-UT/2026/group23/`.
- **Limit:** persistence depends on the course relay and on the repository paths staying the same, because the rules redirect to files on the `main` branch.

### F2 Rich metadata (Met)

- `metadata/dataset-record.ttl` states title, description, licence, publisher, keywords, theme, language, version, landing page, contact point, source (the Kaggle link), issued and modified dates.
- Each distribution record states title, description, licence, access URL, download URL, media type and file format.
- Validation checks F1, F4 and F5 pass.
- **Limit:** the RDF distribution has no byte size. This is the one remaining validation warning.

### F3 Metadata include the identifier of the data (Met)

- Both distribution records carry the W3ID link in `dcat:downloadURL` and `dcat:accessURL`.
- The dataset record and both distribution records carry their own W3ID identifier (checks F3, F4 and F5 pass).

### F4 Registered or indexed in a searchable resource (Partial)

- The FAIR Data Point (version 1.18.0, as the course requires) was installed by Person 1. It holds the dataset record and the two distribution records, which are exported to `metadata/`.
- The repository is public on GitHub and has a README that describes the dataset.
- **Limit:** the FAIR Data Point runs on a local machine (the record IRIs start with `http://localhost:8080`). The records cannot be found by anyone else, and they are not registered in any catalogue or search engine.

## 4. Accessible

### A1 Retrievable by identifier with a standard protocol (Met)

- All nine W3ID addresses redirect over HTTPS and end with HTTP 200 after three hops (w3id.org, the course relay, GitHub). They were tested with `curl`.
- A1.1: HTTPS is open, free and universally implementable.
- A1.2: no authentication is needed, because the repository is public.
- `scripts/check_w3id_rules.py` checks the rules against the real files and reports "All local checks passed."
- **Limit:** the addresses redirect straight to the raw files, so there is no content negotiation. A browser and a program both receive the same file.

### A2 Metadata stay available when the data are gone (Partial)

- The three metadata records are plain Turtle files in the repository (`metadata/`). They do not depend on the local FAIR Data Point.
- **Limit:** data and metadata live in the same repository. If the repository is removed, both are gone. No snapshot was deposited in a long-term archive and there is no DOI.

## 5. Interoperable

### I1 Formal, shared language (Met)

- The data are RDF in Turtle: `data/rdf/library.ttl`, 39,890 triples, parsed by rdflib (check A).
- The metadata are DCAT in Turtle. The shapes are SHACL in Turtle.
- Media types are IANA links (`text/csv`, `text/turtle`) and file formats are links from the EU Publications Office file type list.

### I2 FAIR vocabularies (Met)

- Schema.org is used wherever it fits: `Book`, `Person`, `Organization`, `AggregateRating`, `name`, `author`, `datePublished`, `genre`, `inLanguage`, `keywords`.
- SKOS is used for genres and sections. DCAT and Dublin Core terms are used for the metadata.
- Own terms are added only where Schema.org has no fit: 3 classes and 5 properties in `ontology/library-ontology.ttl`, each with label, comment, domain and range.
- Every `lib:` term used in the data is declared in the ontology (check C4). The ontology is published at the persistent address `.../ont` and was loaded into WebProtégé to check how it reads.
- **Limit:** the licence of the ontology (CC BY 4.0) is a proposed default that both authors still have to confirm (see R1.1).

### I3 Qualified references to other data (Met)

- 1,912 of 2,077 books (92.1%) are linked to their Open Library work with `schema:sameAs`.
- 797 authors (763 persons and 34 organisations) are linked to their Open Library author record.
- Precision was checked by hand on 30 randomly chosen matches: 30 of 30 were correct. With only 30 samples, the true precision could still be as low as about 89% (95% Wilson interval).
- Linking points and example queries are in `documentation/ontology-and-mapping.md`, section 7.
- **Limits:**
    - Only one external dataset is linked.
    - The 12 Rare Books could not be matched, and 165 books in total have no match.
    - The links are identity links (`schema:sameAs`) only.
    - Genre and section concepts are not linked to external vocabularies.

## 6. Reusable

### R1 Richly described, accurate attributes (Met)

- 13 fields per book, described in `data/README.md` (data dictionary) and in `documentation/ontology-and-mapping.md` (mapping table and 19 decisions with reasons).
- The SHACL book shape checks every one of the 2,077 books (check B passes). Self-tests show that invalid books are rejected: year 2999, negative price, missing title, language in capitals, author as plain text, bad catalogue position.
- Missing values stay missing: a blank cell produces no triple, and nothing is imputed.
- **Limits:** the ISBN is filled for only 177 books and none is a valid ISBN-13, so it is published as `lib:recordedIsbn`. The price has no currency. The rating scale (1 to 5) is assumed.

### R1.1 Clear usage licence (Partial)

- The source dataset is under the MIT licence (Kaggle page), stated in the README and in the dataset and distribution records (`dcterms:license`).
- The ontology file declares CC BY 4.0.
- **Limits:**
    - There is no `LICENSE` file in the repository.
    - The README states only the licence of the source dataset, not a licence for the project's own documentation and other created artifacts.
    - The ontology licence is a proposed default, not yet confirmed by both authors.

### R1.2 Detailed provenance (Met)

- The original CSV is kept unchanged (`data/library_catalogue_original.csv`), and the dataset record names the Kaggle source (`dcterms:source`).
- The OpenRefine history (59 operations) is in `documentation/openrefine-operations.json` and explained in `documentation/cleaning-methodology.md`.
- The text repairs are scripted and logged cell by cell: 794 changes in `data/patch_log.csv`.
- The RDF is built by a script and re-running it gives the same file (sha256 `99cdac61051937628e625e1c824186fd94be7fa98154bbbe82a9f9d25c8f5710`).
- For every book the Open Library search keeps the matched identifiers, the similarity score and the status (`data/openlibrary_links.csv`).
- **Limit:** the provenance is kept in files and text. It is not written as PROV-O statements in the metadata.

### R1.3 Community standards (Met)

- Schema.org, DCAT, Dublin Core terms, SKOS, SHACL and Turtle are used, together with the FAIR Data Point version 1.18.0 that the course requires.
- Media types come from the IANA registry, file formats and the theme from EU Publications Office lists, and identifiers from W3ID.
- **Limit:** no library-specific bibliographic standard (such as BIBFRAME) is used. Genre and section labels come from the source catalogue.

## 7. Open items

1. **F4, A2:** make the FAIR Data Point reachable from outside, or register the records in a searchable catalogue.
2. **A2:** deposit a snapshot of the repository in a long-term archive with a DOI.
3. **R1.1:** confirm the licences with both authors, add a `LICENSE` file and state the licence of the project's own documentation and other created artifacts in the README.
4. **F2:** add the byte size (2,662,894) to the RDF distribution record to clear the last validation warning (optional).
5. **Schemas:** the exported FAIR Data Point records still follow the default profiles. Making the FAIR Data Point schemas identical to `shapes/dataset-shape.ttl` and `shapes/distribution-shape.ttl` is open (see `documentation/ontology-and-mapping.md`, section 10).
6. **Organisations:** review the 35 authors that were typed as organisations by name patterns.

## 8. Check it yourself

Run from the root folder of the repository.

    python scripts/validate.py --selftest
    python scripts/check_w3id_rules.py w3id/rules/FAIR-course-UT/2026/group23 --repo-root .
    curl -sIL https://w3id.org/FAIR-course-UT/2026/group23/dataset | grep -i "^HTTP"
