#!/usr/bin/env python3
# Copyright (c) 2026 glry2ua
# To start open cli and go to the folder where you'd like to save files, then run:
# cli command: python3 mirror_cse101.py
# replace "cse101" everywhere with the name of your class folder, e.g., "cse101sp26"
# and update ROOT to the full path to that folder on the server.
import os
import re
import time
from email.utils import formatdate
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

# Root url from which you'd like to download files.
ROOT = "https://insertfullpathhere.edu/professor/classfolder"
# Local directory to save files. Will mirror structure under ROOT.
OUT_DIR = "CSE101_mirror"
SLEEP_SECONDS = 1.1

# Apache autoindex size tokens like: 764, 4.7K, 1.0K, 554K, 12M, 1.2G
SIZE_RE = re.compile(r"^\d+(\.\d+)?[KMG]?$", re.IGNORECASE)


def normalize_url(u: str) -> str:
    """Remove fragments and queries so the same page isn't crawled repeatedly (e.g., ?C=N;O=D)."""
    p = urlparse(u)
    return urlunparse(p._replace(fragment="", query=""))


def httpdate_from_mtime(path: str) -> str:
    """Convert local file mtime -> HTTP date string for If-Modified-Since."""
    return formatdate(timeval=os.path.getmtime(path), usegmt=True)


def local_dir_for(url: str) -> str:
    """
    Map a URL under ROOT to a local directory under OUT_DIR.
    We keep structure starting at /cse101/.
    """
    path = urlparse(url).path
    marker = "/cse101/"
    i = path.find(marker)
    rel = path[i + 1:] if i != -1 else path.lstrip("/")  # "cse101/..."
    return os.path.join(OUT_DIR, rel)


def choose_save_path(url: str, content_type: str | None) -> tuple[str, bool]:
    """
    Decide the local path for this URL.
    Returns (local_path, is_html_page).

    Rule:
    - If it looks like a directory URL (ends with '/' OR last path segment has no dot),
      save as .../index.html.
    - Otherwise save as the direct file path.
    """
    ctype = (content_type or "").lower()
    is_html = "text/html" in ctype

    p = urlparse(url)
    base = os.path.basename(p.path)

    looks_like_dir = url.endswith("/") or base == "" or "." not in base

    local_dir = local_dir_for(url)

    if looks_like_dir and is_html:
        return os.path.join(local_dir, "index.html"), True

    # normal file (or html file with .html in name)
    return local_dir, is_html


def extract_links(html: bytes, base_url: str) -> list[str]:
    """
    Extract links from HTML (href/src), turn into absolute URLs, and normalize.
    """
    soup = BeautifulSoup(html, "html.parser")
    found: list[str] = []

    # <a href="...">
    for a in soup.find_all("a"):
        href = a.get("href")
        if href:
            found.append(urljoin(base_url, href))

    # <img src="...">, <script src="...">
    for tag in soup.find_all(["img", "script"]):
        src = tag.get("src")
        if src:
            found.append(urljoin(base_url, src))

    # <link href="..."> (CSS/icons)
    for link in soup.find_all("link"):
        href = link.get("href")
        if href:
            found.append(urljoin(base_url, href))

    return [normalize_url(u) for u in found]


def classify_autoindex_link(a_tag) -> str:
    """
    On Apache 'Index of ...' pages:
    - href ending in '/' => directory
    - otherwise, if the row ends with a size token => file (even if no extension)
    - else unknown
    """
    href = a_tag.get("href", "")
    if href.endswith("/"):
        return "dir"

    line = a_tag.parent.get_text(" ", strip=True)
    tokens = line.split()
    size_token = tokens[-1] if tokens else ""
    if SIZE_RE.match(size_token):
        return "file"

    return "unknown"


def fetch(session: requests.Session, url: str) -> requests.Response | None:
    """
    Fetch URL with resume behavior:
    - If local file exists, send If-Modified-Since so server can reply 304.
    """
    # Do a lightweight GET with conditional header when possible
    headers = {}
    # We don't know content-type before request, so guess save path from URL structure.
    # This is OK because we only use it for If-Modified-Since and it’s conservative.
    guessed_base = os.path.basename(urlparse(url).path)
    guessed_looks_dir = url.endswith("/") or guessed_base == "" or "." not in guessed_base
    guessed_local = local_dir_for(url)
    if guessed_looks_dir:
        guessed_local = os.path.join(guessed_local, "index.html")

    if os.path.exists(guessed_local):
        headers["If-Modified-Since"] = httpdate_from_mtime(guessed_local)

    try:
        r = session.get(url, timeout=30, headers=headers, allow_redirects=True)
        # 304 is not an error: means "use your local copy"
        if r.status_code == 304:
            return r
        r.raise_for_status()
        return r
    except requests.RequestException as e:
        print("Skip:", url, f"[{e}]")
        return None


def save_bytes(path: str, content: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content)


def crawl():
    session = requests.Session()
    session.headers.update({"User-Agent": "cse101-mirror/1.1 (polite)"})

    queue: list[str] = [normalize_url(ROOT)]
    seen: set[str] = set()

    while queue:
        url = normalize_url(queue.pop(0))

        if not url.startswith(ROOT):
            continue
        if url in seen:
            continue
        seen.add(url)

        r = fetch(session, url)
        if r is None:
            continue

        final_url = normalize_url(r.url)

        # Keep redirects inside tree; if redirect goes outside, ignore it
        if not final_url.startswith(ROOT):
            continue

        ctype = (r.headers.get("Content-Type") or "")
        save_path, is_html = choose_save_path(final_url, ctype)

        if r.status_code == 304:
            # Not modified: keep local copy.
            # Still parse local HTML to keep crawling stable (optional, but helps discover links consistently).
            if is_html and os.path.exists(save_path):
                with open(save_path, "rb") as f:
                    html = f.read()
                html_links = extract_links(html, final_url)
                for nxt in html_links:
                    if nxt.startswith(ROOT):
                        queue.append(nxt)
            continue

        # Save new/updated content
        if not os.path.exists(save_path):
            save_bytes(save_path, r.content)
            print("Saved:", save_path)
        else:
            # If server returned 200 but file exists, overwrite (it changed)
            save_bytes(save_path, r.content)
            print("Updated:", save_path)

        time.sleep(SLEEP_SECONDS)

        if not is_html:
            continue

        soup = BeautifulSoup(r.content, "html.parser")
        pre = soup.find("pre")  # Apache autoindex often uses <pre>

        # If autoindex, classify links so extensionless files are downloaded correctly
        if pre:
            for a in pre.find_all("a"):
                href = a.get("href")
                if not href or href in ("../",) or href.startswith("#") or href.startswith("mailto:"):
                    continue

                nxt = normalize_url(urljoin(final_url, href))
                if not nxt.startswith(ROOT):
                    continue

                kind = classify_autoindex_link(a)
                if kind == "dir":
                    # Ensure directory URLs have trailing slash
                    if not nxt.endswith("/"):
                        nxt += "/"
                    queue.append(nxt)
                else:
                    queue.append(nxt)

        # Also extract normal HTML links (assets + regular links)
        for nxt in extract_links(r.content, final_url):
            if nxt.startswith("mailto:") or nxt.startswith("javascript:"):
                continue
            if nxt.startswith(ROOT):
                queue.append(nxt)


if __name__ == "__main__":
    crawl()
