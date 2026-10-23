#!/usr/bin/env python3
"""
patch_csv.py  (Person 2 helper, documents every change it makes)

Reads the OpenRefine export and applies two small repairs that were missed:
  1. Impossible publication years (later than this year) are blanked.
  2. Mojibake (double-encoded accents, e.g. 'GrÃƒÂ¨ce' -> 'Grèce') is repaired with ftfy.

Nothing else is touched. Every change is written to a log so the repair is
reproducible and can be cited as provenance (FAIR R1.2).

Usage:
  python scripts/patch_csv.py data/library_catalogue_clean.csv \
         data/library_catalogue_repaired.csv data/patch_log.csv
"""
import csv, sys, datetime
import ftfy

TEXT_COLUMNS = ["title", "author", "genre", "section", "subjects", "isbn", "language"]
THIS_YEAR = datetime.date.today().year


def main(src, dst, log_path):
    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    log = []
    for row in rows:
        pos = row["catalogue_position"]

        # 1. impossible years
        y = row["year_published"].strip()
        if y:
            try:
                if int(float(y)) > THIS_YEAR:
                    log.append((pos, "year_published", y, "", f"year later than {THIS_YEAR}"))
                    row["year_published"] = ""
            except ValueError:
                log.append((pos, "year_published", y, "", "not a number"))
                row["year_published"] = ""

        # 2. mojibake
        for col in TEXT_COLUMNS:
            old = row[col]
            if not old:
                continue
            new = ftfy.fix_encoding(old)  # only repairs encoding damage, nothing else
            if new != old:
                log.append((pos, col, old, new, "mojibake repaired"))
                row[col] = new

    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    with open(log_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["catalogue_position", "column", "old_value", "new_value", "reason"])
        w.writerows(log)

    by_reason = {}
    for _, col, _, _, why in log:
        by_reason[(col, why)] = by_reason.get((col, why), 0) + 1
    print(f"rows written: {len(rows)}")
    for (col, why), n in sorted(by_reason.items()):
        print(f"  {col:15s} {why:35s} {n}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
