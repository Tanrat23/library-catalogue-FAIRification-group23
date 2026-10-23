# W3ID for group 23

The course registered the prefix `https://w3id.org/FAIR-course-UT/` and runs a relay for it. Our namespace is:

`https://w3id.org/FAIR-course-UT/2026/group23/`

We write redirect rules as an `.htaccess` file with a `tests.yaml`, and send them as a pull request to the course repository https://github.com/luizbonino/pid-relay. The checks run automatically. If they pass, the rules go live within a few minutes. Nobody reviews them by hand.

## Our identifiers

| identifier | resolves to |
|---|---|
| `.../group23/ont` | the ontology (Turtle). Terms are `ont#Term` |
| `.../group23/data` | the RDF data (Turtle). Records are `data#book-<catalogue position>` |
| `.../group23/dataset` | the project page on GitHub |
| `.../group23/distribution/original-csv` | the original CSV (download) |
| `.../group23/distribution/ttl` | the FAIRified RDF (download) |
| `.../group23/shapes/dataset`, `/shapes/distribution`, `/shapes/book` | the SHACL shapes |

The rules and tests are in `w3id/rules/FAIR-course-UT/2026/group23/`, in the same layout as the course repository.

## Steps, in order

1. Put the files in the project repository and make it public: the ontology, the RDF data, the original CSV and the shapes. The rule targets must exist.
2. Check the rules against the real folders. Run `python scripts/check_w3id_rules.py w3id/rules/FAIR-course-UT/2026/group23 --repo-root <your clone of the project repository>`. It must say "All local checks passed".
3. Fork https://github.com/luizbonino/pid-relay (the Fork button on GitHub) and clone your fork.
4. In your clone open the folder `rules/FAIR-course-UT/2026/group23`.
5. Copy `.htaccess` and `tests.yaml` from `w3id/rules/FAIR-course-UT/2026/group23/` into it. On a Mac, Finder hides files that start with a dot: press Cmd+Shift+. (full stop) to show them.
6. Open the `OWNERS.yaml` in that folder and set `github: [prutha9603, Tanrat23]`. Keep everything else in the file as it is.
7. Commit, push to your fork and open a pull request to `luizbonino/pid-relay`. Only one of you opens it. Claim only group 23.
8. Wait for the check called "validate". The first pull request may wait for the instructor to approve it.
9. If it fails, open Details and the step "Lint and test all rules on Apache httpd". Each problem lists a file and a line. Fix it on the same branch and push again.
10. When it is green, wait a couple of minutes and test the addresses.

## Testing the addresses after they are live

- In a terminal: `curl -sI https://w3id.org/FAIR-course-UT/2026/group23/ont`. You should see a 302 and a `location:` line with the raw GitHub file.
- To follow every hop: `curl -sIL https://w3id.org/FAIR-course-UT/2026/group23/ont`.
- In a browser: https://fair-testbed.eemcs.utwente.nl/pid-manager/resolve
