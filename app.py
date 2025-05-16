import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
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
    check_viewport_meta,
    check_canonical_link,
    check_social_meta,
    check_hreflang_tags,
    check_resource_count,
    check_lazy_loading,
    check_caching_headers,
    check_total_weight,
)

# ========== RULES DEFINITION ==========
BEST_PRACTICES = [
    {"id": 1, "category": "Semantic HTML", "description": "Use proper HTML5 semantic tags such as <header>, <nav>, <main>, <article>, <section>, <footer>."},
    {"id": 2, "category": "Structured Data", "description": "Implement Schema.org markup (JSON-LD or Microdata) for key entities."},
    {"id": 3, "category": "Headings Structure", "description": "Logical heading structure (h1-h6)."},
    {"id": 4, "category": "Alt Text for Images", "description": "Descriptive alt text on all <img> tags."},
    {"id": 5, "category": "Use Lists and Tables", "description": "Proper HTML lists/tables with headers."},
    {"id": 6, "category": "Language Attribute", "description": "Specify the lang attribute on <html> tag."},
    {"id": 7, "category": "Text Transcripts/AR Captions", "description": "Provide transcripts and/or captions for video and audio."},
]

# ========== EVALUATION FUNCTIONS ==========
# (imported from ai_readiness.evaluations)

# ========== STREAMLIT APP ==========
# ========== NEW SEO, INTERNATIONALIZATION & PERFORMANCE CHECKS ==========

# CLI mode: if run with a URL argument, perform analysis and exit
if __name__ == '__main__' and len(sys.argv) > 1:
    url = sys.argv[1]
    # Optional: output detailed report to file
    out_file = sys.argv[2] if len(sys.argv) > 2 else None
    print(f"CLI mode analysis for: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    checks = [
        {"Rule": "Semantic HTML", **dict(zip(["Pass", "Details"], check_semantic_html(soup)))},
        {"Rule": "Schema.org Markup", **dict(zip(["Pass", "Details"], check_schema_markup(soup)))},
        {"Rule": "Headings Structure", **dict(zip(["Pass", "Details"], check_headings_structure(soup)))},
        {"Rule": "Alt Text for Images", **dict(zip(["Pass", "Details"], check_alt_text(soup)))},
        {"Rule": "Lists/Tables", **dict(zip(["Pass", "Details"], check_lists_and_tables(soup)))},
        {"Rule": "Language Attribute", **dict(zip(["Pass", "Details"], check_language_attribute(soup)))},
        {"Rule": "Transcripts/Captions", **dict(zip(["Pass", "Details"], check_transcripts_captions(soup)))},
        {"Rule": "Viewport Meta", **dict(zip(["Pass", "Details"], check_viewport_meta(soup)))},
        {"Rule": "Canonical Link", **dict(zip(["Pass", "Details"], check_canonical_link(soup)))},
        {"Rule": "Social Meta Tags", **dict(zip(["Pass", "Details"], check_social_meta(soup)))},
        {"Rule": "Hreflang Tags", **dict(zip(["Pass", "Details"], check_hreflang_tags(soup)))},
        {"Rule": "Resource Count", **dict(zip(["Pass", "Details"], check_resource_count(soup)))},
        {"Rule": "Lazy Loading", **dict(zip(["Pass", "Details"], check_lazy_loading(soup)))},
        {"Rule": "Caching Headers", **dict(zip(["Pass", "Details"], check_caching_headers(resp)))},
        {"Rule": "Page Weight", "Pass": True, "Details": "Skipped page weight calculation in CLI mode."},
    ]
    num_passed = sum(c["Pass"] for c in checks)
    total_checks = len(checks)
    score = (num_passed / total_checks) * 100 if total_checks else 0
    print(f"Score: {score:.0f}% ({num_passed}/{total_checks} passed)\n")
    for c in checks:
        status = "✅" if c["Pass"] else "❌"
        print(f"{status} {c['Rule']}: {c['Details']}")
    # Write detailed report if requested
    if out_file:
        report = []
        report.append(f"# AI-Readiness Report\n")
        report.append(f"**URL:** {url}\n")
        report.append(f"**Score:** {score:.0f}% ({num_passed}/{total_checks} passed)\n\n")
        report.append("## Detailed Findings\n\n")
        for c in checks:
            stt = "Pass" if c["Pass"] else "Fail"
            report.append(f"### {c['Rule']}\n")
            report.append(f"- Status: {stt}\n")
            report.append(f"- Details: {c['Details']}\n\n")
        report.append("## Recommendations\n\n")
        failures = [c for c in checks if not c["Pass"]]
        if failures:
            for c in failures:
                report.append(f"- **{c['Rule']}**: {c['Details']}\n")
        else:
            report.append("All checks passed. No recommendations.\n")
        with open(out_file, 'w') as f:
            f.writelines(report)
        print(f"Detailed report written to {out_file}")
    sys.exit(0)

st.set_page_config(
    page_title="AI-Readiness Website Evaluator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI-Readiness Website Evaluator")
st.markdown("Enter a website URL to analyze its AI-readiness and accessibility.")

with st.expander("What is AI-Readiness?", expanded=False):
    st.markdown("""
    **AI-Readiness** refers to how well a website's structure and content can be understood by AI systems including:
    - Search engine crawlers
    - Voice assistants
    - Screen readers
    - Large language models
    
    This tool checks for best practices that make websites more accessible to both AI systems and humans.
    """)

website_url = st.text_input("Enter the URL of the website/page to analyze:", placeholder="https://example.com")

if st.button("Analyze Website"):
    if website_url:
        try:
            with st.spinner("Analyzing website..."):
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                resp = requests.get(website_url, headers=headers)
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
                    {"Rule": "Viewport Meta", **dict(zip(["Pass", "Details"], check_viewport_meta(soup)))},
                    {"Rule": "Canonical Link", **dict(zip(["Pass", "Details"], check_canonical_link(soup)))},
                    {"Rule": "Social Meta Tags", **dict(zip(["Pass", "Details"], check_social_meta(soup)))},
                    {"Rule": "Hreflang Tags", **dict(zip(["Pass", "Details"], check_hreflang_tags(soup)))},
                    {"Rule": "Resource Count", **dict(zip(["Pass", "Details"], check_resource_count(soup)))},
                    {"Rule": "Lazy Loading", **dict(zip(["Pass", "Details"], check_lazy_loading(soup)))},
                    {"Rule": "Caching Headers", **dict(zip(["Pass", "Details"], check_caching_headers(resp)))},
                    {"Rule": "Page Weight", **dict(zip(["Pass", "Details"], check_total_weight(resp, soup, website_url, headers)))},
                ]
                
                df = pd.DataFrame(checks)
                df["Status"] = df["Pass"].apply(lambda p: "✅" if p else "❌")
                
                num_passed = df['Pass'].sum()
                total_checks = len(df)
                score_percentage = (num_passed / total_checks) * 100
                
                # Display Results
                st.subheader("Analysis Results")
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.metric("Score", f"{score_percentage:.0f}%", f"{num_passed}/{total_checks} passed")
                
                with col2:
                    st.dataframe(df[["Status", "Rule", "Details"]], use_container_width=True, hide_index=True)
                
                # Visualize score
                st.progress(score_percentage / 100)
                
                # Recommendations section
                if score_percentage < 100:
                    st.subheader("Recommendations")
                    recommendations = df[~df["Pass"]][["Rule", "Details"]]
                    for _, row in recommendations.iterrows():
                        st.markdown(f"- **{row['Rule']}**: {row['Details']}")
                else:
                    st.success("Perfect! This website follows all AI-readiness best practices.")
                
                # Page HTML structure summary
                with st.expander("Page Structure Summary"):
                    st.markdown("### HTML Structure Overview")
                    st.markdown(f"- **Document Title**: {soup.title.string if soup.title else 'No title found'}")
                    st.markdown(f"- **Meta Description**: {'Present' if soup.find('meta', attrs={'name': 'description'}) else 'Missing'}")
                    st.markdown(f"- **Total Links**: {len(soup.find_all('a'))}")
                    st.markdown(f"- **Total Images**: {len(soup.find_all('img'))}")
                    st.markdown(f"- **Total Scripts**: {len(soup.find_all('script'))}")
                    st.markdown(f"- **Total Styles**: {len(soup.find_all('style'))}")
                
        except Exception as e:
            st.error(f"Error analyzing site: {e}")
    else:
        st.warning("Please enter a valid URL to analyze.")

st.markdown("""
---
**Note:** This is an MVP tool to evaluate website AI-readiness based on accessibility and structural best practices.
""")