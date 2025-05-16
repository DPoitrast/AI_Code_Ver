import requests
from bs4 import BeautifulSoup
import json
import sys

from ai_readiness.evaluations import (
    check_semantic_html,
    check_schema_markup,
    check_headings_structure,
    check_alt_text,
    check_lists_and_tables,
    check_language_attribute,
    check_transcripts_captions,
)

# ========== EVALUATION FUNCTIONS ==========

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