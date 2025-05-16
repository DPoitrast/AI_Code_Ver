#!/usr/bin/env python3
"""
AI-Readiness Website Evaluator
A tool to analyze websites for AI-readiness best practices
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import argparse
import os
from datetime import datetime

# ANSI colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ========== EVALUATION FUNCTIONS ==========

def check_semantic_html(soup):
    tags = ["header", "nav", "main", "article", "section", "footer"]
    found = any(soup.find(tag) for tag in tags)
    return found, "Semantic HTML tags found." if found else "Add semantic HTML5 tags for structure."

def check_schema_markup(soup):
    # Simple check: look for JSON-LD scripts containing 'schema.org'
    schema = soup.find_all("script", type="application/ld+json")
    found = any("schema.org" in script.text.lower() for script in schema if script.text) if schema else False
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
    return found, "All images have alt text." if found else f"{len(images_missing_alt)} of {len(images)} images missing alt text."

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

def analyze_website(url, verbose=False):
    """Analyze a website for AI-readiness best practices"""
    try:
        print(f"{Colors.BLUE}{Colors.BOLD}Analyzing {url}...{Colors.END}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        if verbose:
            print(f"Response status code: {resp.status_code}")
            print(f"Page title: {soup.title.string if soup.title else 'No title found'}")
        
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
        
        # Add status symbol and color
        for check in checks:
            check["Status"] = "✅" if check["Pass"] else "❌"
        
        # Page structure summary
        page_summary = {
            "Title": soup.title.string if soup.title else "No title found",
            "Meta Description": "Present" if soup.find('meta', attrs={'name': 'description'}) else "Missing",
            "Total Links": len(soup.find_all('a')),
            "Total Images": len(soup.find_all('img')),
            "Total Scripts": len(soup.find_all('script')),
            "Total Styles": len(soup.find_all('style')),
        }
        
        # Create results summary
        results = {
            "url": url,
            "score": score_percentage,
            "passed": num_passed,
            "total": total_checks,
            "checks": checks,
            "page_summary": page_summary,
            "recommendations": [f"{check['Rule']}: {check['Details']}" for check in checks if not check["Pass"]],
            "datetime": datetime.now().isoformat()
        }
        
        return results
        
    except Exception as e:
        print(f"{Colors.RED}Error: {str(e)}{Colors.END}")
        return {"error": str(e)}

def print_report(results):
    """Print formatted analysis results to console"""
    if "error" in results:
        print(f"{Colors.RED}Analysis failed: {results['error']}{Colors.END}")
        return
    
    url = results["url"]
    score = results["score"]
    passed = results["passed"]
    total = results["total"]
    
    # Determine score color
    score_color = Colors.RED
    if score >= 80:
        score_color = Colors.GREEN
    elif score >= 50:
        score_color = Colors.YELLOW
    
    # Print header
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}AI-Readiness Analysis for {url}{Colors.END}")
    print("=" * 70)
    
    # Print score
    print(f"\n{Colors.BOLD}Score: {score_color}{score:.1f}%{Colors.END} ({passed}/{total} checks passed)")
    
    # Print check results
    print(f"\n{Colors.BOLD}Check Results:{Colors.END}")
    for check in results["checks"]:
        status_color = Colors.GREEN if check["Pass"] else Colors.RED
        status = check["Status"]
        rule = check["Rule"]
        details = check["Details"]
        print(f"  {status_color}{status}{Colors.END} {rule}: {details}")
    
    # Print page summary
    print(f"\n{Colors.BOLD}Page Summary:{Colors.END}")
    for key, value in results["page_summary"].items():
        print(f"  • {key}: {value}")
    
    # Print recommendations
    if results["recommendations"]:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Recommendations:{Colors.END}")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
    else:
        print(f"\n{Colors.GREEN}{Colors.BOLD}Perfect! This website follows all AI-readiness best practices.{Colors.END}")
    
    print("\n" + "=" * 70)

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(
        description="AI-Readiness Website Evaluator - Analyze websites for AI accessibility best practices"
    )
    parser.add_argument("url", help="URL of the website to analyze")
    parser.add_argument("-o", "--output", help="Output file path for JSON results")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Analyze website
    results = analyze_website(args.url, args.verbose)
    
    # Print report
    print_report(results)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results saved to {args.output}")
    else:
        # Default output file in the reports directory
        os.makedirs("reports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = args.url.replace("http://", "").replace("https://", "").replace("/", "_").strip("_")
        filename = f"reports/{domain}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nFull results saved to {filename}")

if __name__ == "__main__":
    main()