# pdf2epub

Convert PDF books and scientific papers into well-formatted EPUB files suitable for reading on e-readers (especially Kindle).

## Overview

`pdf2epub` provides a two-phase pipeline for high-quality PDF to EPUB conversion:

1. **Marker Phase** ([marker-pdf](https://github.com/VikParuchuri/marker)): A deep learning pipeline that visually parses the PDF and extracts it into standard Markdown, cleanly isolating images and formatting mathematical equations into LaTeX.

2. **Pandoc Phase**: The universal document converter takes Marker's Markdown output, renders the LaTeX math into SVG (the default, broadly compatible format) or MathML, embeds local images, and packages everything into an EPUB structure.

## Features

- 🎯 **High-Quality Conversion**: Preserves formatting, images, and mathematical equations
- 📚 **E-Reader Optimized**: Generates EPUBs optimized for Kindle and other e-readers
- 🔬 **Scientific Papers**: Handles LaTeX math rendering (SVG by default, MathML optional)
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
3. **PyTorch** (required by marker-pdf): Install a version compatible with your hardware **before** installing `pdf2epub` to ensure GPU acceleration works correctly. See [pytorch.org/get-started](https://pytorch.org/get-started/locally/) for instructions.
   - **GPU (CUDA)**: `pip install torch --index-url https://download.pytorch.org/whl/cu121`
   - **CPU only**: `pip install torch`

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
pdf2epub paper.pdf --title "Research Paper"
```

**Use MathML instead of SVG (not recommended for Kindle):**
```bash
pdf2epub paper.pdf --math-format mathml --title "Research Paper"
```

**Save intermediate Markdown (for debugging):**
```bash
pdf2epub input.pdf --save-markdown output.md
```

**Set EPUB language:**
```bash
pdf2epub input.pdf --language fr
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
  --language en \
  --save-markdown my-book.md \
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
    math_format="svg",  # default; use "mathml" if your e-reader prefers it
    language="en",      # BCP 47 language tag (default: "en")
    save_markdown="output.md"  # optional; saves intermediate Markdown for debugging
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
| `--math-format` | Math rendering format (`mathml` or `svg`) | `svg` |
| `--language` | BCP 47 language tag for the EPUB (e.g. `en`, `fr`, `de`) | `en` |
| `--save-markdown` | Save intermediate Markdown file to this path | None |
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
│  • Renders LaTeX to SVG (or MathML) │
│  • Embeds images                    │
│  • Adds metadata and cover          │
│  • Generates table of contents      │
└─────────────────────────────────────┘
    ↓
EPUB Output
```

### Math Rendering

- **SVG** (default): Renders equations as scalable vector graphics embedded in the EPUB. Broadly compatible with e-readers including Kindle, which does not support MathML natively.
- **MathML**: Alternative rendering using structured mathematical markup. Supported by some e-readers (e.g., Apple Books) but **not** recommended for Kindle.

### Kindle Compatibility

`pdf2epub` sets several EPUB metadata fields required for reliable Kindle delivery and display:

- **Language** (`dc:language`): Always included (default `en`). A missing language is a known cause of Kindle error 999. Use `--language` to set the correct BCP 47 tag for your document (e.g. `fr` for French, `de` for German).
- **Publication date** (`dc:date`): Always set to today's date in ISO 8601 format. Pandoc only emits `dc:date` when the variable is explicitly provided; without it the field is absent, which violates the EPUB spec recommendation and can trigger validation errors on some Kindle devices.
- **Last-modified timestamp** (`dcterms:modified`): Required by the EPUB 3.2 spec. Pandoc auto-generates this using the current UTC time.
- **Unique identifier** (`dc:identifier`): Required by the EPUB spec. Pandoc automatically generates a UUID for each EPUB.
- **Title** (`dc:title`): Use `--title` to set a descriptive title. Without a title, some Kindle devices show the filename instead.
- **Math as SVG**: The default `--math-format svg` is recommended for Kindle because Kindle does not support MathML.

## Dependencies

### Python Packages
- **marker-pdf**: PDF to Markdown conversion with deep learning
- **pypandoc**: Python wrapper for Pandoc
- **click**: Command-line interface framework

### System Dependencies
- **Pandoc**: Universal document converter (must be installed separately)

### Marker Dependencies
marker-pdf relies on heavy vision transformer models and requires PyTorch. Key points:
- **Model size**: The ML models downloaded on first run are approximately **2–4 GB**. Ensure you have sufficient disk space.
- **GPU (recommended)**: marker-pdf typically requires **3–5 GB of VRAM**. Install a CUDA-compatible PyTorch before installing `pdf2epub` (see [Prerequisites](#prerequisites)).
- **CPU fallback**: marker-pdf will run on CPU if no GPU is available, but expect **significantly longer conversion times**. Large documents may also exhaust system RAM and cause the process to crash.

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

### First run is slow / downloading models
marker-pdf downloads vision transformer models on first run (**~2–4 GB**). Subsequent runs are much faster.

### Slow conversion or process crash on CPU
marker-pdf uses deep learning models that run much faster on a GPU (3–5 GB VRAM recommended). Without a GPU:
- Conversion of a long document can take many minutes or even hours.
- The process may crash if system RAM is exhausted (marker-pdf can use several GB of RAM).

To speed things up, install a CUDA-enabled PyTorch and ensure your GPU has enough VRAM:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Math equations not rendering
By default, `pdf2epub` uses SVG math rendering via pandoc's `--webtex` option, which fetches rendered SVG equations from an external web service (CodeCogs). This requires an internet connection during conversion. If you are offline, use MathML instead:
```bash
pdf2epub input.pdf --math-format mathml
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
