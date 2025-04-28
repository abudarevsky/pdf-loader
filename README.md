# Rapid PDF Extractor Demo 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Optional: Replace MIT with your license -->

This project demonstrates a high-performance pipeline for extracting information from **text-based PDF documents**. It's designed to showcase typical skills involved in AI Engineering, focusing on speed and accuracy for specific extraction tasks.

## ✨ Features

*   **Speed Optimized:** Engineered for maximum speed when processing text-based PDFs.
*   **Text Extraction:** Reliably extracts textual content, preserving some structure in Markdown format.
*   **Table Extraction:** Accurately detects and extracts tabular data into structured formats (e.g., CSV).
*   **Image Caption Detection:** Identifies text segments functioning as captions for images within the document flow.
*   **Image Classification:** Extracts images and classifies them as captioned images and other images (e.g. background).
*   **Performance Logging:** Logs the processing time taken for each page and each extracted image, useful for performance analysis.
*   **Focus on Text-Based PDFs:** Optimized for PDFs containing selectable text, not scanned image-only documents.

## 🧠 AI Engineering Skills Demonstrated

This demo project highlights several core competencies:

*   **Pipeline Orchestration:** Managing a multi-step workflow from PDF input to structured output using a central script (`main.py`).
*   **Modular Design:** Integrating specialized modules for PDF parsing, text processing, table detection, image handling, and AI model inference.
*   **Efficient Tooling:** Leveraging modern, high-performance tools like `uv` for environment and dependency management.
*   **Data Handling:** Processing and structuring diverse data types (text, tables, images, metadata).

## ⚙️ Setup

This project uses `uv` for fast environment and package management.

1.  **Install `uv`:**

    Follow the official installation instructions for `uv` based on your operating system: https://github.com/astral-sh/uv#installation

    *   **macOS / Linux (Recommended):**
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
    *   **Windows (PowerShell):**
        ```powershell
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```
    *   Other methods (pipx, cargo, etc.) are available on the `uv` installation page.

2.  **Install Project Dependencies:**

    Once `uv` is installed, navigate to the project's root directory in your terminal. `uv` will automatically create a virtual environment (usually `.venv`) and install packages listed in `requirements.txt` (or `pyproject.toml`).

    ```bash
    # This command creates/updates the virtual environment and installs packages
    uv sync
    ```
    *(Note: If your dependencies are in a different file, adjust the command or your `pyproject.toml`.)*

## 🚀 Running the Demo

A sample PDF (`docs/GraphletAI-PropertyGraphFactory-Public.pdf`) is included for demonstration. To process this file and generate results in the `output1/` directory, run the main script using `uv run`:

```bash
# Ensure you are in the project's root directory
# This command executes main.py within the uv-managed environment
uv run main.py .
```
This command will process the specified PDF and place the extracted artifacts into the output1 folder.

## 📊 Understanding the Output (`output1/`)

After running the demo command on the sample PDF (`docs/GraphletAI-PropertyGraphFactory-Public.pdf`), the `output1/` directory will be created (if it doesn't exist) and populated with the extraction results.

The key outputs include:


* Page folder includes:
    *   **`content.md`**: Contains the textual page content extracted from the PDF document, formatted using **Markdown** to potentially preserve some structural elements like headings or lists.
        *   **`images/`**: A subdirectory containing the actual image files extracted from the PDF.
        *   The filename of the corresponding image saved in the `images/` subdirectory.
    *   **`images/captions`**: A subdirectory containing the captioned image files extracted from the PDF.
        *   The detected caption associated with an image.
        *   The filename of the corresponding image saved in the `images/` subdirectory.
*   **`tables/`**: A subdirectory containing extracted tables, likely saved as individual files (e.g., `table_1.csv`, `table_2.json`). Each file represents one detected table in a structured format. *(Note: The sample document might not contain tables)*.

### Output Summary for Sample PDF

The results in the `output1` directory demonstrate the successful extraction capabilities of the pipeline on the provided sample document (`docs/GraphletAI-PropertyGraphFactory-Public.pdf`). Notably:

*   Text content is extracted into Markdown format.
*   Images are successfully identified and saved.
*   **Image captions are correctly detected and associated with their respective images**, as can be verified by examining the extracted content/images for **page 3** and **page 19**.

Review the files within `output1/` to explore the detailed results of the text extraction, table structuring (if any), caption detection, and image classification performed on the sample document.


📄 License
This project is licensed under the MIT License - see the LICENSE file for details. (Create a LICENSE file with the MIT license text if you haven't already, or update if using a different license)