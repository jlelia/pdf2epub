# pdf2epub

Convert PDF books and scientific papers into well-formatted EPUB files suitable for reading on e-readers (especially Kindle).

## Overview

`pdf2epub` provides a two-phase pipeline for high-quality PDF to EPUB conversion:

1. **Marker Phase** ([marker-pdf](https://github.com/VikParuchuri/marker)): A deep learning pipeline that visually parses the PDF and extracts it into standard Markdown, cleanly isolating images and formatting mathematical equations into LaTeX.

2. **Pandoc Phase**: The universal document converter takes Marker's Markdown output, renders the LaTeX math into a Kindle-friendly format (MathML or SVG), embeds local images, and packages everything into an EPUB structure.

## Features

- 🎯 **High-Quality Conversion**: Preserves formatting, images, and mathematical equations
- 📚 **E-Reader Optimized**: Generates EPUBs optimized for Kindle and other e-readers
- 🔬 **Scientific Papers**: Handles LaTeX math rendering (MathML or SVG)
- 🖼️ **Image Support**: Automatically extracts and embeds images
- 📖 **Metadata Support**: Add title, author, and cover images to your EPUBs
- 🎨 **CLI and Python API**: Use from command line or integrate into your Python projects

## Installation

### Prerequisites

1. **Python 3.10+** is required
2. **Pandoc** must be installed separately on your system:
   - **Ubuntu/Debian**: `sudo apt install pandoc`
   - **macOS**: `brew install pandoc`
   - **Windows**: Download from [pandoc.org](https://pandoc.org/installing.html)

### Install pdf2epub

```bash
pip install pdf2epub
```

Or install from source:

```bash
git clone https://github.com/jlelia/pdf2epub.git
cd pdf2epub
pip install .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Command Line

**Basic conversion:**
```bash
pdf2epub input.pdf
```

This creates `input.epub` in the same directory.

**Specify output path:**
```bash
pdf2epub input.pdf -o output.epub
```

**Add metadata:**
```bash
pdf2epub input.pdf --title "My Book" --author "Author Name"
```

**Add cover image:**
```bash
pdf2epub input.pdf --cover cover.jpg
```

**Scientific papers with math:**
```bash
pdf2epub paper.pdf --math-format mathml --title "Research Paper"
```

**Verbose output:**
```bash
pdf2epub input.pdf -v
```

**Full example:**
```bash
pdf2epub book.pdf \
  -o my-book.epub \
  --title "The Great Book" \
  --author "Jane Doe" \
  --cover cover.png \
  --math-format mathml \
  --verbose
```

### Python API

```python
from pdf2epub import convert

# Basic conversion
epub_path = convert("input.pdf")

# With options
epub_path = convert(
    pdf_path="input.pdf",
    output_path="output.epub",
    title="My Book",
    author="Author Name",
    cover="cover.jpg",
    math_format="mathml"  # or "svg"
)

print(f"EPUB created: {epub_path}")
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `INPUT_PDF` | Path to input PDF file (required) | - |
| `-o, --output` | Output EPUB file path | Same name as input with `.epub` |
| `--title` | EPUB title metadata | None |
| `--author` | EPUB author metadata | None |
| `--cover` | Path to cover image | None |
| `--math-format` | Math rendering format (`mathml` or `svg`) | `mathml` |
| `-v, --verbose` | Enable verbose logging | False |
| `--version` | Show version and exit | - |
| `--help` | Show help message | - |

## How It Works

### Architecture

```
PDF Input
    ↓
┌─────────────────────────────────────┐
│  Phase 1: Marker (marker-pdf)       │
│  • Deep learning PDF parser         │
│  • Extracts text and structure      │
│  • Isolates images                  │
│  • Converts to Markdown + LaTeX     │
└─────────────────────────────────────┘
    ↓
Markdown + Images + LaTeX Math
    ↓
┌─────────────────────────────────────┐
│  Phase 2: Pandoc                    │
│  • Converts Markdown to EPUB        │
│  • Renders LaTeX to MathML/SVG      │
│  • Embeds images                    │
│  • Adds metadata and cover          │
│  • Generates table of contents      │
└─────────────────────────────────────┘
    ↓
EPUB Output
```

### Math Rendering

- **MathML** (default): Best for most e-readers including Kindle. Renders equations as proper mathematical markup.
- **SVG**: Alternative rendering using images. Use if your target e-reader doesn't support MathML.

## Dependencies

### Python Packages
- **marker-pdf**: PDF to Markdown conversion with deep learning
- **pypandoc**: Python wrapper for Pandoc
- **click**: Command-line interface framework

### System Dependencies
- **Pandoc**: Universal document converter (must be installed separately)

### Marker Dependencies
marker-pdf requires PyTorch and other ML dependencies. These are automatically installed with marker-pdf, but note that:
- First run may download ML models (~500MB)
- GPU acceleration is optional but recommended for large PDFs

## Testing

Run tests with pytest:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=pdf2epub --cov-report=html

# Run specific test file
pytest tests/test_converter.py

# Verbose output
pytest -v
```

## Troubleshooting

### "pandoc: command not found"
Install Pandoc on your system (see Installation section above).

### "marker-pdf is not installed"
```bash
pip install marker-pdf
```

### First run is slow
Marker downloads ML models on first run (~500MB). Subsequent runs are much faster.

### Math equations not rendering
Try switching math format:
```bash
pdf2epub input.pdf --math-format svg
```

### Low quality output
- Ensure your PDF is text-based, not scanned images
- For scanned PDFs, use OCR preprocessing first
- Try adjusting Marker settings (see marker-pdf documentation)

## Project Structure

```
pdf2epub/
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
├── src/
│   └── pdf2epub/
│       ├── __init__.py         # Package initialization
│       ├── cli.py              # CLI entry point
│       ├── converter.py        # Main orchestration
│       ├── marker_step.py      # Phase 1: PDF → Markdown
│       ├── pandoc_step.py      # Phase 2: Markdown → EPUB
│       └── utils.py            # Utilities
└── tests/
    ├── __init__.py
    ├── test_converter.py       # Converter tests
    ├── test_marker_step.py     # Marker tests
    └── test_pandoc_step.py     # Pandoc tests
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [marker-pdf](https://github.com/VikParuchuri/marker) - Excellent PDF to Markdown conversion
- [Pandoc](https://pandoc.org/) - Universal document converter
- Built with ❤️ for researchers and readers

## Links

- **GitHub**: https://github.com/jlelia/pdf2epub
- **Issues**: https://github.com/jlelia/pdf2epub/issues
- **PyPI**: https://pypi.org/project/pdf2epub/ (coming soon)
