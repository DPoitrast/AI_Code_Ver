# AI-Readiness Website Evaluator

A tool that evaluates websites for AI-readiness and accessibility best practices. It helps identify areas where websites can be improved to be more accessible to AI systems and search engines.

## Features

- Analyzes website HTML for AI-readiness and accessibility best practices
- Provides specific recommendations for improvement
- Displays an overall score and detailed breakdown by category
- Command-line interface with colorful output
- Saves reports in JSON format for further analysis

## Requirements

- Python 3.6+
- Required packages: requests, beautifulsoup4

## Installation

1. Clone this repository:
```bash
git clone https://github.com/DPoitrast/AI_Code_Ver.git
cd ai-code-verification
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x ai_readiness_checker.py
```

## Usage

### Command-line interface

Analyze one or more URLs directly on the command line or provide a file containing URLs:

```bash
./ai_readiness_checker.py https://example.com https://example.org --summary
```

```bash
./ai_readiness_checker.py --urls-file urls.txt -v
```

### Options

- `-o, --output` &ndash; Directory where JSON reports will be saved (default: `./reports`)
- `-v, --verbose` &ndash; Enable verbose output
- `--urls-file` &ndash; Path to a text file with one URL per line
- `--summary` &ndash; Display a summary of scores when analyzing multiple URLs

Example:
```bash
./ai_readiness_checker.py https://example.com https://example.org -o reports --summary
```

## Web Interface (Optional)

The repository also includes a Streamlit web interface:

```bash
streamlit run app.py
```

## Evaluation Criteria

The tool evaluates websites based on the following criteria:

1. **Semantic HTML** - Use of HTML5 semantic tags for structure
2. **Schema.org Markup** - Implementation of structured data
3. **Headings Structure** - Logical heading hierarchy
4. **Alt Text for Images** - Descriptive alternative text for images
5. **Lists and Tables** - Proper use of HTML lists and tables
6. **Language Attribute** - Specification of language
7. **Transcripts/Captions** - Accessibility for multimedia elements

## License

MIT

