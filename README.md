# Library Catalogue Data FAIRification
FAIRification of a library catalogue dataset using OpenRefine, RDF, semantic metadata and a FAIR Data Point.

<img width="1365" height="630" alt="image" src="https://github.com/user-attachments/assets/97b14589-85d4-4b79-8bc8-fe0b69014d5b" />


## 1. Project overview

This project aims to improve the Findability, Accessibility, Interoperability and Reusability (FAIRness) of a library catalogue dataset.

The project uses OpenRefine for data preparation, RDF for semantic representation, and structured metadata published through a FAIR Data Point.

## 2. Original dataset

- **Dataset name:** Library Catalogue
- **Original source:** [Dataset Source](https://www.kaggle.com/datasets/neramarkovi/library-catalog)
- **Original format:** CSV
- **Original record count:** 2,104, before any documented row removals
- **Original license and reuse conditions:** [MIT](https://www.mit.edu/~amini/LICENSE.md)

## 3. Data preparation

The catalogue was cleaned using OpenRefine. 
The cleaning decisions, field definitions and validation results are documented in the `documentation/` directory.

- The OpenRefine export has 2,077 books and 13 columns ([`data/library_catalogue_clean.csv`](data/library_catalogue_clean.csv)).
- A script then repairs the broken accents and the impossible years that were left, and logs all 794 changes ([`scripts/patch_csv.py`](scripts/patch_csv.py), [`data/patch_log.csv`](data/patch_log.csv)).
- A second script converts the repaired file to RDF: 39,890 triples in [`data/rdf/library.ttl`](data/rdf/library.ttl) ([`scripts/build_rdf.py`](scripts/build_rdf.py)).

## 4. Repository structure

- [`data/`](data/): original CSV, cleaned and repaired CSV, repair log, Open Library links, and the RDF/Turtle representation of the catalogue in `data/rdf/`
- [`ontology/`](ontology/): project-specific ontology
- [`shapes/`](shapes/): SHACL shapes for books, Dataset records and Distribution records
- [`metadata/`](metadata/): exported FAIR Data Point metadata records (one Dataset and two Distributions)
- [`w3id/`](w3id/): W3ID redirect rules and their tests
- [`scripts/`](scripts/): Python scripts that repair, convert, link and validate the data
- [`documentation/`](documentation/): cleaning methodology, ontology and mapping, pipeline, FAIR assessment and validation log
- `requirements.txt`: Python packages needed by the scripts

The final report is handed in through Canvas.

### Documentation

- [`data/README.md`](data/README.md): files, data dictionary and known data issues
- [`documentation/cleaning-methodology.md`](documentation/cleaning-methodology.md): OpenRefine cleaning decisions
- [`documentation/openrefine-operations.json`](documentation/openrefine-operations.json): the recorded OpenRefine operations
- [`documentation/ontology-and-mapping.md`](documentation/ontology-and-mapping.md): semantic model, mapping decisions, RDF examples, Open Library links and validation
- [`documentation/rdf-pipeline.md`](documentation/rdf-pipeline.md): the commands that rebuild and check everything
- [`documentation/fair-assessment.md`](documentation/fair-assessment.md): FAIR self assessment
- [`documentation/validation_log.txt`](documentation/validation_log.txt): output of the validation script
- [`w3id/README.md`](w3id/README.md): W3ID rules and the steps to publish them

## 5. Semantic model and persistent identifiers

**Group number:** 23

**Namespace:** https://w3id.org/FAIR-course-UT/2026/group23/

| what | persistent address |
|---|---|
| Ontology (terms are `ont#Term`) | https://w3id.org/FAIR-course-UT/2026/group23/ont |
| Data namespace (records are `data#book-<catalogue_position>`) | https://w3id.org/FAIR-course-UT/2026/group23/data |
| Dataset | https://w3id.org/FAIR-course-UT/2026/group23/dataset |
| Original CSV (download) | https://w3id.org/FAIR-course-UT/2026/group23/distribution/original-csv |
| RDF in Turtle (download) | https://w3id.org/FAIR-course-UT/2026/group23/distribution/ttl |
| SHACL shapes | https://w3id.org/FAIR-course-UT/2026/group23/shapes/dataset, https://w3id.org/FAIR-course-UT/2026/group23/shapes/distribution, https://w3id.org/FAIR-course-UT/2026/group23/shapes/book |

The redirect rules are merged in the course relay. All nine addresses were tested and end with HTTP 200. The rules and their tests are in [`w3id/`](w3id/).

## 6. Metadata publication

The Dataset and Distribution metadata are held in a FAIR Data Point (version 1.18.0).

FDP URL: not available. The FAIR Data Point runs on a local machine.

The three records are exported to [`metadata/`](metadata/):

- [`dataset-record.ttl`](metadata/dataset-record.ttl)
- [`distribution-original-csv.ttl`](metadata/distribution-original-csv.ttl)
- [`distribution-rdf.ttl`](metadata/distribution-rdf.ttl)

## 7. Interoperability

The catalogue records are linked with an external bibliographic dataset using `schema:sameAs`.

External dataset: Open Library

Integration findings:

- 1,912 of 2,077 books (92.1%) are linked to their Open Library work, and 797 authors to their Open Library author record.
- 30 randomly chosen matches were checked by hand and all 30 were correct.
- Linking points and example queries are in [`documentation/ontology-and-mapping.md`](documentation/ontology-and-mapping.md), section 7.

## 8. License and attribution

Original dataset source and license: [MIT](https://www.mit.edu/~amini/LICENSE.md)

Licences of the project's own files (full text in [`LICENSE`](LICENSE)):

- **MIT:** `data/`, `metadata/`, `scripts/` and `w3id/`
- **CC BY 4.0:** `ontology/`, `shapes/`, `documentation/` and the README files ([https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/))
## 9. Citation

**Dataset source**

Library Catalog. Uploaded by Nera Marković. Kaggle. Available at: [Dataset](https://www.kaggle.com/datasets/neramarkovi/library-catalog). Accessed: 19/09/2026.

**Note:** No DOI was provided on the source page. This citation identifies the original dataset using its available source information.
