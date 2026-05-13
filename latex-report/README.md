# CSKG Report - LaTeX Template

> LaTeX report for **Constructing Cybersecurity Knowledge Graphs from Unstructured Intelligence**.

This repository contains the LaTeX source for the CSKG report based on the Springer **LLNCS** class.

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/vityasyyy/cskg.git
cd cskg/latex-report
```

### 2. Compile the Report

```bash
make
```

This generates `cskg_report.pdf`.

---

## Prerequisites

Choose one of the following options:

### Option A: Local TeX Live

- **macOS**: `brew install --cask mactex`
- **Windows**: Install [MiKTeX](https://miktex.org/download) or [TeX Live](https://tug.org/texlive/)
- **Linux (Debian/Ubuntu)**: `sudo apt-get install texlive-full`

> Make sure `pdflatex` and `bibtex` are available in your `PATH`.

### Option B: Docker (No local TeX Live required)

Ensure [Docker](https://www.docker.com/products/docker-desktop) is installed.

```bash
make docker
```

---

## Repository Structure

```
latex-report/
├── cskg_report.tex           # Main document
├── references.bib            # Bibliography database
├── llncs.cls                 # Springer LLNCS class file
├── splncs04.bst              # Springer bibliography style
├── fig1.eps                  # Sample figure
├── Makefile                  # Build automation
├── README.md                 # This file
└── sections/
    ├── introduction.tex
    ├── related_work.tex
    ├── proposed_approach.tex
    ├── implementation.tex
    ├── use_cases.tex
    ├── conclusion.tex
    └── appendix.tex
```

---

## Compilation

### Using Make

```bash
make          # Compile the report
make clean    # Remove auxiliary files
```

### Manual Compilation

If you prefer to compile manually:

```bash
pdflatex cskg_report.tex
bibtex cskg_report
pdflatex cskg_report.tex
pdflatex cskg_report.tex
```

### Docker Compilation

```bash
make docker   # Compile inside a Docker container
```

---

## Customizing the Report

1. **Update metadata** in `cskg_report.tex`:

   ```tex
   \title{Your Title Here}
   \author{Author One \and Author Two}
   \institute{Your Institution}
   ```

2. **Write content** by editing the files in `sections/`.

3. **Add figures** to the root folder (or a `figures/` directory) and use:

   ```tex
   \includegraphics[width=\textwidth]{filename}
   ```

4. **Update references** in `references.bib`.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `llncs.cls` not found | Ensure `llncs.cls` is in the same directory as `cskg_report.tex` |
| References shown as `[?]` | Run `bibtex cskg_report` then `pdflatex cskg_report.tex` two more times |
| Figure not found | Check that the image file exists and the path is correct |
| `pdflatex` command not found | Install TeX Live or use `make docker` |
| EPS figure issues | Try converting EPS to PDF or use `epstopdf` package |

---

## References

- [Springer LNCS Author Guidelines](https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines)
- [LaTeX Project](https://www.latex-project.org/)
- [CSKG Project Repository](https://github.com/vityasyyy/cskg)

---

## License

This LaTeX template follows the structure provided by Springer. The report content is the property of the respective authors.
