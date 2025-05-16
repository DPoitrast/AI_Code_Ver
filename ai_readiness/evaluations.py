"""Common evaluation checks for AI-readiness."""
import requests
from bs4 import BeautifulSoup

# Basic structure and accessibility checks

def check_semantic_html(soup: BeautifulSoup):
    tags = ["header", "nav", "main", "article", "section", "footer"]
    found = any(soup.find(tag) for tag in tags)
    return found, "Semantic HTML tags found." if found else "Add semantic HTML5 tags for structure."

def check_schema_markup(soup: BeautifulSoup):
    # Check for JSON-LD or Microdata schema.org structured data
    script_ld = soup.find_all("script", type="application/ld+json")
    found_json_ld = any("schema.org" in script.text for script in script_ld)
    tags_microdata = soup.find_all(attrs={"itemscope": True})
    found_microdata = any(
        tag.get("itemtype") and "schema.org" in tag.get("itemtype")
        for tag in tags_microdata
    )
    found = found_json_ld or found_microdata
    if found:
        details = []
        if found_json_ld:
            details.append("JSON-LD found")
        if found_microdata:
            details.append("Microdata markup found")
        return True, "; ".join(details)
    return False, "Add JSON-LD or Microdata schema.org structured data."

def check_headings_structure(soup: BeautifulSoup):
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    found = bool(headings)
    return found, f"{len(headings)} heading tags found." if found else "Add descriptive headings (h1-h6)."

def check_alt_text(soup: BeautifulSoup):
    images = soup.find_all("img")
    images_missing_alt = [img for img in images if not img.has_attr("alt") or not img["alt"].strip()]
    found = len(images_missing_alt) == 0 and len(images) > 0
    return found, "All images have alt text." if found else f"{len(images_missing_alt)} images missing alt text."

def check_lists_and_tables(soup: BeautifulSoup):
    lists = soup.find_all(["ul", "ol"])
    tables = soup.find_all("table")
    found = bool(lists or tables)
    return found, f"{len(lists)} lists, {len(tables)} tables found." if found else "Consider using lists and tables for structured content."

def check_language_attribute(soup: BeautifulSoup):
    html_tag = soup.find("html")
    found = html_tag and html_tag.has_attr("lang")
    return found, "lang attribute present on html tag." if found else "Add lang attribute for language declaration."

def check_transcripts_captions(soup: BeautifulSoup):
    videos = soup.find_all("video")
    audios = soup.find_all("audio")
    found = True
    if videos or audios:
        found = all((v.get("aria-label") or v.get("title") or v.find("track", attrs={"kind": "captions"})) for v in videos)
        found = found and all((a.get("aria-label") or a.get("title")) for a in audios)
    return found, "Multimedia elements have ARIA labels/titles/captions." if found else "Provide captions/transcripts for videos/audio."

# Additional SEO, internationalization and performance checks

def check_viewport_meta(soup: BeautifulSoup):
    tag = soup.find("meta", attrs={"name": "viewport"})
    found = bool(tag)
    return found, "Viewport meta tag present." if found else "Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> for mobile responsiveness."

def check_canonical_link(soup: BeautifulSoup):
    tag = soup.find("link", rel="canonical") or soup.find("link", attrs={"rel": "canonical"})
    found = bool(tag and tag.get("href"))
    return found, f"Canonical link found: {tag['href']}" if found else "Add <link rel=\"canonical\" href=\"...\"> to avoid duplicate content issues."

def check_social_meta(soup: BeautifulSoup):
    og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
    twitter_tag = soup.find("meta", attrs={"name": "twitter:card"})
    found = bool(og_tags and twitter_tag)
    details = []
    if og_tags:
        details.append(f"{len(og_tags)} OpenGraph tags")
    else:
        details.append("Missing OpenGraph tags")
    if twitter_tag:
        details.append("Twitter Card tag present")
    else:
        details.append("Missing Twitter Card tag")
    return found, "; ".join(details)

def check_hreflang_tags(soup: BeautifulSoup):
    tags = soup.find_all("link", rel="alternate", hreflang=True)
    found = bool(tags)
    return found, f"{len(tags)} hreflang tags found." if found else "Add <link rel=\"alternate\" hreflang=\"x\" href=\"...\"> tags for multilingual support."

def check_resource_count(soup: BeautifulSoup):
    resources = []
    resources += [tag['src'] for tag in soup.find_all('script', src=True)]
    resources += [tag['href'] for tag in soup.find_all('link', rel='stylesheet', href=True)]
    resources += [tag['src'] for tag in soup.find_all('img', src=True)]
    resources += [tag['src'] for tag in soup.find_all('video', src=True)]
    resources += [tag['src'] for tag in soup.find_all('audio', src=True)]
    count = len(resources)
    found = count <= 50
    return found, f"{count} external resources referenced."

def check_lazy_loading(soup: BeautifulSoup):
    images = soup.find_all('img', src=True)
    if not images:
        return True, "No images to lazy-load."
    missing = [img for img in images if img.get('loading') != 'lazy']
    found = len(missing) == 0
    return found, f"{len(missing)}/{len(images)} images lack loading=\"lazy\"."

def check_caching_headers(resp):
    headers = resp.headers
    has_cache = 'Cache-Control' in headers
    has_etag = 'ETag' in headers
    found = has_cache or has_etag
    details = []
    if has_cache:
        details.append(f"Cache-Control: {headers.get('Cache-Control')}")
    else:
        details.append("Missing Cache-Control header")
    if has_etag:
        details.append(f"ETag: {headers.get('ETag')}")
    else:
        details.append("Missing ETag header")
    return found, '; '.join(details)

def check_total_weight(resp, soup: BeautifulSoup, base_url: str, headers):
    import urllib.parse
    total_size = len(resp.content)
    resources = []
    resources += [tag['src'] for tag in soup.find_all('script', src=True)]
    resources += [tag['href'] for tag in soup.find_all('link', rel='stylesheet', href=True)]
    resources += [tag['src'] for tag in soup.find_all('img', src=True)]
    resources += [tag['src'] for tag in soup.find_all('video', src=True)]
    resources += [tag['src'] for tag in soup.find_all('audio', src=True)]
    for url in resources:
        abs_url = urllib.parse.urljoin(base_url, url)
        try:
            head = requests.head(abs_url, headers=headers, allow_redirects=True, timeout=5)
            size = int(head.headers.get('Content-Length', 0))
            total_size += size
        except Exception:
            continue
    found = total_size <= 2 * 1024 * 1024  # 2MB threshold
    human = f"{total_size/1024:.1f} KB"
    return found, f"Total page weight: {human} (including HTML & resources)"

__all__ = [name for name in globals() if name.startswith('check_')]
