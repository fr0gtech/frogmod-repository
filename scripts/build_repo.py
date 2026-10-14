#!/usr/bin/env python3
"""Build repo.json, the file Frogtech Mod Loader reads, from mods.json and this GitHub repository's releases.

For each mod in mods.json, the newest release asset named <id>_v<version>.zip (or .vpk) becomes its download: the
version, url, size and sha256 come from the asset, everything else from mods.json. Run by the GitHub Action on every
release; run it yourself with GITHUB_REPOSITORY=owner/repo [GITHUB_TOKEN=...] python3 scripts/build_repo.py.
No dependencies beyond Python 3.9.
"""
import hashlib
import json
import os
import re
import sys
import urllib.request

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")
ASSET = re.compile(r"^([a-z0-9_-]{1,64})_v(\d+(?:\.\d+)*)\.(zip|vpk)$")
ID = re.compile(r"^[a-z0-9_-]{1,64}$")


def get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "frogmod-repository", "Accept": "application/octet-stream" if raw else "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read() if raw else json.load(r)


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def releases(repo):
    out, page = [], 1
    while True:
        batch = get(f"{API}/repos/{repo}/releases?per_page=100&page={page}")
        out += [r for r in batch if not r.get("draft")]
        if len(batch) < 100:
            return out
        page += 1


def build(source, repo):
    if source.get("format") != 1 or not source.get("name") or not isinstance(source.get("mods"), list):
        raise SystemExit("mods.json needs format 1, a name and a mods list")
    newest = {}   # mod id -> (version, asset)
    for rel in releases(repo):
        for a in rel.get("assets", []):
            m = ASSET.match(a["name"])
            if m and (m.group(1) not in newest or vkey(m.group(2)) > vkey(newest[m.group(1)][0])):
                newest[m.group(1)] = (m.group(2), a)
    mods = []
    for mod in source["mods"]:
        mid = mod.get("id", "")
        if not ID.match(mid) or not mod.get("name"):
            raise SystemExit(f"mod {mid!r}: needs an id (a-z, 0-9, _ and -) and a name")
        if mid not in newest:
            print(f"warning: no release asset named {mid}_v<version>.zip for {mid}; left out", file=sys.stderr)
            continue
        version, asset = newest[mid]
        body = get(asset["url"], raw=True)
        entry = {k: v for k, v in mod.items() if k not in ("version", "url", "sha256", "size")}
        entry.update(version=version, url=asset["browser_download_url"], size=len(body), sha256=hashlib.sha256(body).hexdigest())
        mods.append(entry)
        print(f"{mid} {version}: {len(body)} bytes")
    return {**{k: v for k, v in source.items() if k != "mods"}, "mods": mods}


def main():
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise SystemExit("set GITHUB_REPOSITORY=owner/repo")
    source = json.load(open("mods.json", encoding="utf-8"))
    out = build(source, repo)
    os.makedirs("site", exist_ok=True)
    with open("site/repo.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"site/repo.json: {len(out['mods'])} mods")


if __name__ == "__main__":
    main()
