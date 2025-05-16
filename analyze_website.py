from ai_readiness.analysis import analyze_website

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m ai_readiness.analysis [URL]")
        sys.exit(1)
    url = sys.argv[1]
    results = analyze_website(url)
    print(results)
