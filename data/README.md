# Data folder

This folder holds every data file of the library catalogue project, from the original Kaggle CSV to the final RDF.
Run all commands from the root folder of the repository.

## 1. Source

- **Dataset:** "Library Catalog", uploaded by Nera Marković on Kaggle
- **Link:** https://www.kaggle.com/datasets/neramarkovi/library-catalog
- **Licence stated by the source:** MIT
- **Accessed:** 19/09/2026
- **DOI:** none on the source page

## 2. Files in this folder

| file | what it is | size | made by |
|---|---|---|---|
| `library_catalogue_original.csv` | The Kaggle file, unchanged. First distribution of the dataset. | 2,104 rows, 18 columns, 1,569,933 bytes | Kaggle |
| `library_catalogue_clean.csv` | The OpenRefine export. Input of the pipeline. | 2,077 rows, 13 columns, 1,359,063 bytes | OpenRefine (Person 1) |
| `library_catalogue_repaired.csv` | The clean file after two small repairs: broken accents and impossible years. | 2,077 rows, 13 columns, 1,328,713 bytes | `scripts/patch_csv.py` |
| `patch_log.csv` | One line for every cell the repair step changed. | 794 changes, 1,467,886 bytes | `scripts/patch_csv.py` |
| `openlibrary_links.csv` | The saved answer of the Open Library search, one line per book. | 2,077 rows, 251,187 bytes | `scripts/link_openlibrary.py` |
| `openlibrary_links_review_sample.csv` | 30 random matches, checked by hand. | 30 rows, 3,772 bytes | `scripts/link_openlibrary.py` |
| `rdf/library.ttl` | The catalogue as RDF (Turtle). Second distribution of the dataset. | 39,890 triples, 2,662,894 bytes | `scripts/build_rdf.py` |

## 3. How the files are made

1. `library_catalogue_original.csv` is cleaned in OpenRefine (59 recorded operations, see `documentation/openrefine-operations.json` and `documentation/cleaning-methodology.md`). The result is `library_catalogue_clean.csv`.
2. `scripts/patch_csv.py` repairs what OpenRefine left behind and writes `library_catalogue_repaired.csv` and `patch_log.csv`.
3. `scripts/link_openlibrary.py` searches Open Library and writes `openlibrary_links.csv`.
4. `scripts/build_rdf.py` reads the repaired CSV and the links file and writes `rdf/library.ttl`.

Rows removed during cleaning: 27 (7 with a blank `catalogue_position`, 10 with a duplicate `catalogue_position`, 10 with a blank `title`). 2,104 minus 27 is 2,077.
Columns removed during cleaning: `Total-copies`, `Last borrowed_date`, `Page count`, `Dimensions`, `Thumbnail`.

## 4. Data dictionary (`library_catalogue_repaired.csv`)

"Filled" counts the rows where the cell is not blank. A blank cell means the value is missing in the source. No value was invented.

| column | original name | type | filled | notes |
|---|---|---|---|---|
| `catalogue_position` | `catalog Position` | text | 2077 | Unique code of the book, for example A1-B1-0001. The book IRI is built from it. |
| `title` | `Title` | text | 2077 | |
| `author` | `author` | text | 2077 | Author name as written in the source. |
| `year_published` | `Year Published` | integer | 2072 | 1200 to 2019. Blank for 5 books. |
| `genre` | `genre` | text | 2026 | 43 distinct labels after the merges, for example Drama or Poetry. |
| `section` | `Section` | text | 2019 | 9 values: Fiction, Children, Humanities, Non-Fiction, Young Adult, Reference, History, Science, Rare Books. |
| `times_borrowed` | `Times borrowed` | integer | 2071 | 0 to 2,256. |
| `ratings` | `Rating` | decimal | 1759 | Rating value, 1.03 to 5.0. The source text said "out of 5 stars". |
| `ratings_count` | `Ratings count` | integer | 1735 | Number of ratings, 1 to 918. |
| `price` | `Price` | decimal | 1882 | 0.09 to 95,000. The "$" sign of the source text was removed. No currency is asserted in the RDF. |
| `language` | `Language` | text | 2075 | Lowercase language code, 23 distinct codes, for example en, fr, de. |
| `isbn` | `ISBN` | text | 177 | Every value has 12 digits, so none is a valid ISBN-13. Kept as recorded. |
| `subjects` | `subjects` | text | 2027 | Free text, kept whole. |

## 5. Known data issues

- **Impossible years:** the OpenRefine export still holds two (A2-B3-0024 is 2999 and A4-B3-0082 is 2119). `patch_csv.py` blanks them and logs it, so the repaired CSV and the RDF contain no year later than 2026. The repaired file has 5 blank years: 3 from OpenRefine and these 2.
- **Broken accents:** 792 cells were repaired and logged: 771 in `subjects`, 11 in `title`, 10 in `author`. With the 2 years this makes the 794 lines of `patch_log.csv`.
- **ISBN:** only 177 books have one, and none is a valid ISBN-13. The RDF stores it as `lib:recordedIsbn`, not as `schema:isbn`.
- **Price:** 195 books have no price. 24 values are above 1000, 12 of them first editions in the Rare Books section. They are kept as in the source.
- **Rating scale:** assumed to be 1 to 5. Observed values range from 1.03 to 5.0.
- **Books without a section:** 58. They stay without a section.
- **Books without a genre:** 51.

## 6. Open Library links

`openlibrary_links.csv` has one line per book.

| column | meaning |
|---|---|
| `catalogue_position`, `title`, `author` | the book as in the catalogue |
| `work_key`, `author_key` | Open Library identifiers of the matched work and author |
| `matched_title`, `matched_author` | what Open Library calls the match. Kept only to check the match. |
| `first_publish_year` | year given by Open Library |
| `score` | similarity of the title |
| `status` | `matched` (1,912 books) or `no_match` (165 books) |

- A match is accepted only when the title is at least 90 percent similar and the author agrees (same surname, or a name at least 85 percent similar).
- The RDF stores only the Open Library identifiers, as `schema:sameAs`. No Open Library text is copied into it.
- `openlibrary_links_review_sample.csv` has the extra column `correct_yes_no`. The 30 sampled matches were opened one by one and all 30 were judged correct (same title and author, any edition).

## 7. Rebuild and check

    python scripts/patch_csv.py data/library_catalogue_clean.csv data/library_catalogue_repaired.csv data/patch_log.csv
    python scripts/build_rdf.py data/library_catalogue_repaired.csv data/rdf/library.ttl --base https://w3id.org/FAIR-course-UT/2026/group23/ --links data/openlibrary_links.csv
    python scripts/validate.py --selftest

- Re-running the build gives the same file every time. Check it with `shasum -a 256 data/rdf/library.ttl`. The expected value is `99cdac61051937628e625e1c824186fd94be7fa98154bbbe82a9f9d25c8f5710`.
- All steps, with the Python setup, are in `documentation/rdf-pipeline.md`.

## 8. Licence

- The source dataset is under the MIT licence, as stated on its Kaggle page.
- The dataset record and both distribution records in `metadata/` state the MIT licence (`https://spdx.org/licenses/MIT`).
