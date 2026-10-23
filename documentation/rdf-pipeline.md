# How to rebuild the RDF (Person 2)

This page lists the commands that turn Person 1's cleaned CSV into the RDF file and check it.
Run every command from the root folder of the repository.

## Files the pipeline uses

| file | who made it | role |
|---|---|---|
| `data/library_catalogue_original.csv` | Person 1 | the original Kaggle file, first distribution |
| `data/library_catalogue_clean.csv` | Person 1 | OpenRefine export, input of the pipeline |
| `data/library_catalogue_repaired.csv` | `scripts/patch_csv.py` | the export after the text repairs |
| `data/patch_log.csv` | `scripts/patch_csv.py` | every cell the repair step changed |
| `data/rdf/library.ttl` | `scripts/build_rdf.py` | the catalogue as RDF, second distribution |

## Commands, in order

    python3 -m venv ~/fair-venv
    source ~/fair-venv/bin/activate
    pip install -r requirements.txt
    python scripts/patch_csv.py data/library_catalogue_clean.csv data/library_catalogue_repaired.csv data/patch_log.csv
    python scripts/build_rdf.py data/library_catalogue_repaired.csv data/rdf/library.ttl --base https://w3id.org/FAIR-course-UT/2026/group23/
    python scripts/validate.py --selftest | tee documentation/validation_log.txt
    python scripts/check_w3id_rules.py w3id/rules/FAIR-course-UT/2026/group23 --repo-root .
    python scripts/link_openlibrary.py data/library_catalogue_repaired.csv data/openlibrary_links.csv --email you@example.org --limit 40
    python scripts/draw_ontology.py ontology/library-ontology.ttl documentation/ontology-diagram   (needs Graphviz: the dot program)

- The virtual environment lives in your home folder (`~/fair-venv`), outside the repository, so it can never be committed by mistake.
- The Open Library lookup cache also lives in your home folder.
- The Open Library step is optional. Run `build_rdf.py` again with `--links data/openlibrary_links.csv` afterwards to add the links.

## What a correct run prints

- `build_rdf.py` writes 2077 books and 37,172 triples (without Open Library links).
- `validate.py --selftest` ends with "All checks passed."
- `check_w3id_rules.py` ends with "All local checks passed."

## Related pages

- Ontology, mapping decisions and RDF examples: `documentation/ontology-and-mapping.md`
- Persistent identifiers and the pull request to the course relay: `w3id/README.md`
