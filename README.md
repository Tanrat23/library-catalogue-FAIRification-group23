# library-catalogue-FAIRification-group23
FAIRification of a library catalogue dataset using OpenRefine, RDF, semantic metadata and a FAIR Data Point.

## 1. Project overview

This project aims to improve the Findability, Accessibility, Interoperability and Reusability (FAIRness) of a library catalogue dataset.

The project uses OpenRefine for data preparation, RDF for semantic representation, and structured metadata published through a FAIR Data Point.

## 2. Original dataset

- **Dataset name:** Library Catalogue
- **Original source:** https://www.kaggle.com/datasets/neramarkovi/library-catalog
- **Original format:** CSV
- **Original record count:** 2,104, before any documented row removals
- **Original license and reuse conditions:** # Released under MIT License

Copyright (c) 2013 Mark Otto.

Copyright (c) 2017 Andrew Fong.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

The original dataset is stored separately from the cleaned version, subject to the source's redistribution conditions.

## 3. Data preparation

The catalogue was cleaned using OpenRefine. The process included [describe the transformations actually performed].

The cleaning decisions, field definitions and validation results are documented in the `documentation/` directory.

## 4. Repository structure

- `data/original/` — original dataset, subject to its license
- `data/fairified/` — cleaned tabular dataset
- `data/rdf/` — RDF/Turtle representation of the catalogue
- `ontology/` — project-specific ontology
- `metadata-schemas/` — Dataset and Distribution metadata schemas
- `fdp-metadata/` — exported FAIR Data Point metadata records
- `documentation/` — data dictionary, cleaning methodology and evaluation
- `report/` — final project report

## 5. Semantic model and persistent identifiers

**Group number:** 23

**Ontology IRI:**
https://w3id.org/FAIR-course-UT/2025-2026/group23/ont

**Data namespace:**
https://w3id.org/FAIR-course-UT/2025-2026/group23/data#

These are the planned identifiers. Their resolution status will be documented after the W3ID redirects have been configured and tested.

## 6. Metadata publication

The Dataset and Distribution metadata will be published through a FAIR Data Point.

FDP URL: [Add once available]

## 7. Interoperability

The project will investigate linking catalogue records with an external bibliographic dataset using ISBN and other suitable bibliographic properties.

External dataset: Open Library

Integration findings: [Add results after testing]

## 8. License and attribution

Original dataset source and license: [Add verified details]

License applicable to the project's own documentation and other created artifacts: [Add the licence agreed upon by the group]

## 9. Citation

[Add a recommended citation for the dataset and the final repository version.]
