#!/usr/bin/env python3
"""
check_w3id_rules.py  -  a quick local check of the redirect rules before you open the pull request.

It does NOT replace the course checks (those run w3id.org's checker and a real Apache server on the
pull request). It catches the common mistakes listed in the course student guide, and it runs every
test in tests.yaml against the rules in plain Python, so a mismatch between a rule and its test shows up
in seconds instead of after a failed pull request.

Checks:
  1. only allowed directives, https targets, allowed status codes (301, 302, 303, 307)
  2. no comment at the end of a rule line, no leading slash in a pattern, no "^(.+)/?$" pattern
  3. every test in tests.yaml gives the expected status and location when run against the rules
  4. every rule is used by at least one test
  5. (optional) every target that points into the repository points to a file that exists in your clone

Usage (from the repo root):
  python scripts/check_w3id_rules.py w3id/rules/FAIR-course-UT/2026/group23
  python scripts/check_w3id_rules.py w3id/rules/FAIR-course-UT/2026/group23 --repo-root /path/to/your/clone
"""
import argparse, os, re, sys
import yaml

ALLOWED_DIRECTIVES = {"rewriteengine", "rewritecond", "rewriterule", "rewritebase", "redirect",
                      "redirectmatch", "header", "addtype", "<ifmodule", "</ifmodule>", "options"}
ALLOWED_CODES = {301, 302, 303, 307}
NAMESPACE = "https://w3id.org/FAIR-course-UT/2026/"

problems = []


def fail(msg):
    problems.append(msg)
    print(f"[FAIL] {msg}")


def ok(msg):
    print(f"[PASS] {msg}")


def parse_rules(path):
    rules = []
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        directive = line.split()[0].lower()
        if directive not in ALLOWED_DIRECTIVES:
            fail(f".htaccess line {n}: directive '{line.split()[0]}' is not allowed")
            continue
        if directive != "rewriterule":
            continue
        m = re.match(r"^RewriteRule\s+(\S+)\s+(\S+)\s*(\[[^\]]*\])?\s*(.*)$", line, re.I)
        if not m:
            fail(f".htaccess line {n}: cannot read this RewriteRule")
            continue
        pattern, target, flags, rest = m.groups()
        if rest.strip():
            fail(f".htaccess line {n}: text after the flags (a comment at the end of a rule line is not allowed)")
        if pattern.startswith("/") or pattern.startswith("^/"):
            fail(f".htaccess line {n}: pattern '{pattern}' must not start with a slash")
        if pattern in ("^(.+)/?$", "^(.*)/?$"):
            fail(f".htaccess line {n}: pattern '{pattern}' swallows the trailing slash")
        if not target.startswith("https://"):
            fail(f".htaccess line {n}: target must be an absolute https URL")
        code = re.search(r"R=(\d+)", flags or "")
        code = int(code.group(1)) if code else 302
        if code not in ALLOWED_CODES:
            fail(f".htaccess line {n}: status {code} is not allowed (use 301, 302, 303 or 307)")
        rules.append({"line": n, "pattern": pattern, "target": target, "code": code, "tests": 0})
    return rules


def run_tests(rules, tests_path):
    data = yaml.safe_load(open(tests_path, encoding="utf-8"))
    tests = (data or {}).get("tests") or []
    if not tests:
        fail("tests.yaml has no tests")
    for i, t in enumerate(tests, 1):
        if "pid" in t:
            if not t["pid"].startswith(NAMESPACE):
                fail(f"test {i}: pid does not start with {NAMESPACE}")
                continue
            rel = t["pid"][len(NAMESPACE):].split("/", 1)[1] if "/" in t["pid"][len(NAMESPACE):] else ""
        else:
            rel = t.get("path", "")
        label = f"test {i} ({rel or 'namespace root'})"
        hit = next((r for r in rules if re.match(r["pattern"], rel)), None)
        if hit is None:
            if t.get("status") == 404:
                ok(f"{label}: no rule matches, 404 expected")
            else:
                fail(f"{label}: no rule matches this path")
            continue
        hit["tests"] += 1
        good = True
        if "status" in t and t["status"] != hit["code"]:
            fail(f"{label}: expected status {t['status']}, rules give {hit['code']}")
            good = False
        if "location" in t and t["location"] != hit["target"]:
            fail(f"{label}: expected location {t['location']}, rules give {hit['target']}")
            good = False
        if "location_regex" in t and not re.search(t["location_regex"], hit["target"]):
            fail(f"{label}: location_regex does not match {hit['target']}")
            good = False
        if good:
            ok(f"{label}: {hit['code']} to {hit['target'].split('/main/')[-1] if '/main/' in hit['target'] else hit['target']}")
    for r in rules:
        if r["tests"] == 0:
            fail(f"rule on line {r['line']} ({r['pattern']}) has no test")


def check_repo(rules, repo_root):
    for r in rules:
        m = re.search(r"/raw/[^/]+/(.+)$", r["target"])
        if not m:
            continue
        rel = m.group(1)
        if os.path.isfile(os.path.join(repo_root, rel)):
            ok(f"file exists in your clone: {rel}")
        else:
            fail(f"file NOT found in your clone: {rel}  (rule on line {r['line']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--repo-root", help="your clone of the project repository, to check the target files exist")
    args = ap.parse_args()
    rules = parse_rules(os.path.join(args.folder, ".htaccess"))
    ok(f"{len(rules)} RewriteRule lines read") if rules else fail("no RewriteRule found")
    run_tests(rules, os.path.join(args.folder, "tests.yaml"))
    if args.repo_root:
        check_repo(rules, args.repo_root)
    print()
    if problems:
        print(f"{len(problems)} problem(s) found")
        sys.exit(1)
    print("All local checks passed. The pull request runs the full checks on a real Apache server.")


if __name__ == "__main__":
    main()
