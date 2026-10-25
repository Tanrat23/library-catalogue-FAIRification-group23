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

## 4. Repository structure

- `data` — original dataset, cleaned tabular dataset and RDF/Turtle representation of the catalogue
- `documentation/` — cleaning methodology and evaluation
- `metadata/` —  metadata schemas exported from FDP.
- `ontology/` — project-specific ontology
- `scripts/` — python scripts related to execution of project requirements
- `shapes/` — dataset and distribution metadata schemas
- `w3id/` — W3ID rules and identifiers
- `report/` — final project report

## 5. Semantic model and persistent identifiers

**Group number:** 23

**Ontology:**
[https://w3id.org/FAIR-course-UT/2025-2026/group23/ont](https://w3id.org/FAIR-course-UT/2026/group23/ont#)

**Data namespace:**
[https://w3id.org/FAIR-course-UT/2025-2026/group23/data#](https://w3id.org/FAIR-course-UT/2026/group23/data# 	)


## 6. Metadata publication

The Dataset and Distribution metadata has been created using a FAIR Data Point locally.

## 7. Interoperability

The project will investigate linking catalogue records with an external bibliographic dataset using suitable bibliographic properties.

External dataset: Open Library

## 8. License and attribution

Original dataset source and license: [MIT](https://www.mit.edu/~amini/LICENSE.md)

## 9. Citation

**Dataset source**

Library Catalog. Uploaded by Nera Marković. Kaggle. Available at: [Dataset](https://www.kaggle.com/datasets/neramarkovi/library-catalog). Accessed: 19/09/2026.

**Note:** No DOI was provided on the source page. This citation identifies the original dataset using its available source information.
