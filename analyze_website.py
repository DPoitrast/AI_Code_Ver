import requests
from bs4 import BeautifulSoup
import json
import sys

# ========== EVALUATION FUNCTIONS ==========

def check_semantic_html(soup):
    tags = ["header", "nav", "main", "article", "section", "footer"]
    found = any(soup.find(tag) for tag in tags)
    return found, "Semantic HTML tags found." if found else "Add semantic HTML5 tags for structure."

def check_schema_markup(soup):
    # Simple check: look for JSON-LD scripts containing 'schema.org'
    schema = soup.find_all("script", type="application/ld+json")
    found = any("schema.org" in script.text.lower() for script in schema)
    return found, "Schema.org markup present." if found else "Add Schema.org structured data."

def check_headings_structure(soup):
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    found = bool(headings)
    return found, f"{len(headings)} heading tags found." if found else "Add descriptive headings (h1-h6)."

def check_alt_text(soup):
    images = soup.find_all("img")
    if not images:
        return True, "No images found."
    images_missing_alt = [img for img in images if not img.has_attr('alt') or not img['alt'].strip()]
    found = len(images_missing_alt) == 0
    return found, "All images have alt text." if found else f"{len(images_missing_alt)} images missing alt text."

def check_lists_and_tables(soup):
    lists = soup.find_all(['ul', 'ol'])
    tables = soup.find_all("table")
    found = bool(lists or tables)
    return found, f"{len(lists)} lists, {len(tables)} tables found." if found else "Consider using lists and tables for structured content."

def check_language_attribute(soup):
    html_tag = soup.find("html")
    found = html_tag and html_tag.has_attr('lang')
    return found, "lang attribute present on html tag." if found else "Add lang attribute for language declaration."

def check_transcripts_captions(soup):
    # For MVP: flag if there are audio/video tags without descriptions/captions
    videos = soup.find_all("video")
    audios = soup.find_all("audio")
    found = True  # assume pass if no multimedia
    if videos or audios:
        found = all((v.get('aria-label') or v.get('title') or v.find('track', attrs={'kind': 'captions'})) for v in videos)
        found = found and all((a.get('aria-label') or a.get('title')) for a in audios)
    return found, "Multimedia elements have ARIA labels/titles/captions." if found else "Provide captions/transcripts for videos/audio."

def analyze_website(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # -- Evaluation Results --
        checks = [
            {"Rule": "Semantic HTML", **dict(zip(["Pass", "Details"], check_semantic_html(soup)))},
            {"Rule": "Schema.org Markup", **dict(zip(["Pass", "Details"], check_schema_markup(soup)))},
            {"Rule": "Headings Structure", **dict(zip(["Pass", "Details"], check_headings_structure(soup)))},
            {"Rule": "Alt Text for Images", **dict(zip(["Pass", "Details"], check_alt_text(soup)))},
            {"Rule": "Lists/Tables", **dict(zip(["Pass", "Details"], check_lists_and_tables(soup)))},
            {"Rule": "Language Attribute", **dict(zip(["Pass", "Details"], check_language_attribute(soup)))},
            {"Rule": "Transcripts/Captions", **dict(zip(["Pass", "Details"], check_transcripts_captions(soup)))},
        ]
        
        # Calculate score
        num_passed = sum(1 for check in checks if check["Pass"])
        total_checks = len(checks)
        score_percentage = (num_passed / total_checks) * 100
        
        # Add status symbol
        for check in checks:
            check["Status"] = "✅" if check["Pass"] else "❌"
        
        # Create results summary
        results = {
            "url": url,
            "score": score_percentage,
            "passed": num_passed,
            "total": total_checks,
            "checks": checks,
            "recommendations": [f"{check['Rule']}: {check['Details']}" for check in checks if not check["Pass"]]
        }
        
        return results
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_website.py [URL]")
        sys.exit(1)
    
    url = sys.argv[1]
    results = analyze_website(url)
    
    # Save results to file
    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary to console
    print(f"\nAnalysis Complete for {url}")
    print(f"Score: {results['score']:.1f}% ({results['passed']}/{results['total']} checks passed)")
    
    if results.get('recommendations'):
        print("\nRecommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
    else:
        print("\nPerfect! This website follows all AI-readiness best practices.")
    
    print(f"\nFull results saved to analysis_results.json")
