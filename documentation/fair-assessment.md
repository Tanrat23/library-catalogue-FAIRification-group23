# FAIR Assessment: Library Catalogue Dataset

## 1. Findable (F)
* **Before:** The original dataset was discoverable only through Kaggle's internal search ecosystem. It lacked a globally unique, persistent identifier (PID) and relied on basic platform-specific metadata.
* **After:** The dataset and its distributions are now assigned globally unique and persistent W3ID identifiers (e.g., `https://w3id.org/FAIR-course-UT/2026/group23/dataset`). Rich, machine-readable metadata via a FAIR Data Point, makes the resource independently discoverable.

## 2. Accessible (A)
* **Before:** Accessing the original CSV required navigating a proprietary platform and potentially logging into a user account.
* **After:** The dataset and its metadata are retrievable by their W3ID identifiers using standard, open HTTP protocols. The W3ID relay automatically resolves to publicly accessible raw download links hosted on GitHub.

## 3. Interoperable (I)
* **Before:** The data was provided as a flat CSV file relying entirely on plain text strings. It lacked formal, accessible, shared, and broadly applicable semantic vocabularies.
* **After:** The cleaned dataset is transformed into an RDF Linked Data format (Turtle). It utilizes established semantic web vocabularies (such as Schema.org) and a custom domain ontology to explicitly define relationships between books, authors, genres, and library sections.

## 4. Reusable (R)
* **Before:** The dataset contained incomplete records (such as missing titles) and lacked detailed, machine-readable provenance or license attachments.
* **After:** The data has been cleaned to remove unusable records, with all transformations recorded in `cleaning-methodology.md`. The metadata now explicitly includes data provenance (`dcterms:source`) and a clear usage license, ensuring it meets domain-relevant community standards for reuse.
