# Library Catalogue Data FAIRification
FAIRification of a library catalogue dataset using OpenRefine, RDF, semantic metadata and a FAIR Data Point.

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

## 4. Repository structure

- `data/original/` — original dataset, cleaned tabular dataset and RDF/Turtle representation of the catalogue
- `ontology/` — project-specific ontology
- `metadata-schemas/` — Dataset and Distribution metadata schemas
- `fdp-metadata/` — exported FAIR Data Point metadata records
- `documentation/` — cleaning methodology and evaluation
- `report/` — final project report

## 5. Semantic model and persistent identifiers

**Group number:** 23

**Ontology:**
https://w3id.org/FAIR-course-UT/2025-2026/group23/ont

**Data namespace:**
https://w3id.org/FAIR-course-UT/2025-2026/group23/data#

These are the planned identifiers. Their resolution status will be documented after the W3ID redirects have been configured and tested.

## 6. Metadata publication

The Dataset and Distribution metadata will be published through a FAIR Data Point.

FDP URL: [Add once available]

## 7. Interoperability

The project will investigate linking catalogue records with an external bibliographic dataset using suitable bibliographic properties.

External dataset: Open Library

Integration findings: [Add results after testing]

## 8. License and attribution

Original dataset source and license: [MIT](https://www.mit.edu/~amini/LICENSE.md)

License applicable to the project's own documentation and other created artifacts: [Add the licence agreed upon by the group]

## 9. Citation

[Add a recommended citation for the dataset and the final repository version.]
