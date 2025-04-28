import json
import time
import fitz  # PyMuPDF
import os
import re
import os
import camelot

import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional

import warnings
import spacy

from font_flag import FontFlag
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def pdf_to_markdown(pdf_path, output_md_path):
    """
    Robust PDF to Markdown converter that:
    - Reliably extracts all text content
    - Accurately detects and extracts images
    - Organizes images with captions separately
    - Preserves document structure
    """
    start_time = time.time()
    # Create output directories

    doc = fitz.open(pdf_path)
    page_times = []
    image_times = []
    for page_num in range(len(doc)):
        extract_page_text_and_images(output_md_path, page_times, image_times, page_num, doc)

    end_time = time.time()
    total_time = end_time - start_time
    avg_image_time = sum(image_times) / len(image_times) if image_times else 0

    stats = {
        "document_time": total_time,
        "page_times": page_times,
        "average_image_time": avg_image_time,
    }

    with open(os.path.join(output_md_path, "stats.json"), "w") as f:
        json.dump(stats, f, indent=4) 

def extract_page_text_and_images(output_md_path, page_times, image_times, page_num, doc):
    page_start_time = time.time()

    page = doc.load_page(page_num)
    page_md_dir = f"{output_md_path}/page{page_num+1}"
    page_images_captions_dir = f"{page_md_dir}/images/captions"
    page_images_dir = f"{page_md_dir}/images"

    os.makedirs(page_md_dir, exist_ok=True)        
    os.makedirs(page_images_dir, exist_ok=True)    
    os.makedirs(page_images_captions_dir, exist_ok=True)

    markdown_content = []
    image_counter = 1
    caption_counter = 1

    # Get all page elements (both text and images)
    elements = page.get_text("dict", sort=True)["blocks"]

    # First pass: Identify all potential captions
    potential_captions = []
    images_dict = {}
    cap_idx = []
    page_images = page.get_images()
    prev_font_size = None
    for block in elements:
        if block["type"] == 0:  # Text block
            text = ""
             
            for line in block["lines"]:
                for span in line["spans"]:
                    text += span["text"]
                text += "\n"                
            text = clean_text(text)
            font_size = None
            try:
                # Check if block has lines and spans
                if "lines" in block and len(block["lines"]) > 0:
                    if "spans" in block["lines"][0] and len(block["lines"][0]["spans"]) > 0:
                        font_size = block["lines"][0]["spans"][0].get("size")
            except (KeyError, IndexError) as e:
                print(f"Warning: Couldn't get font size for block {text}: {e}")
                font_size = None

            # Format as heading if large font (heuristic)
            # if font_size and font_size > 11 and len(text) < 100:
            is_title_ = is_title(text)
            if is_title_:
                markdown_content.append(f"\n## {text}\n")
            else:
                markdown_content.append(text + "\n")
            if not prev_font_size:
                prev_font_size = font_size

            if not is_title_ and is_caption(text, block, prev_font_size):
                potential_captions.append({
                        "text": text,
                        "bbox": fitz.Rect(block["bbox"]),
                        "used": False,
                        "font_size": font_size
                    })
            prev_font_size = font_size
        elif block["type"] == 1:
            img_num = block["number"]
            key = str(fitz.Rect(block["bbox"]))

            markdown_content.append(f'![imgcap_{img_num}](imgref_{img_num})\n\n')   
            images_dict[key]=len(markdown_content)-1
        # Second pass: Process all elements
    image_section=False
    for block in elements:
        # Process text blocks
        if block["type"] == 0:
            text = clean_text(block.get("text", ""))
            if not text:
                continue

                # Check if this text is already captured as a caption
            if any(not cap["used"] and cap["text"] == text for cap in potential_captions):
                continue

            # Process image blocks
        elif block["type"] == 1:
            if not page_images:
                continue

            img_start_time = time.time()
            image_bytes = block["image"]

            # Find nearest caption
            img_rect = fitz.Rect(block["bbox"])
            caption = None

            caption = find_nearest_caption(potential_captions, img_rect)
            key = str(img_rect)
            md_idx = images_dict.get(key, None)
            # Determine image path and markdown
            if caption and md_idx is not None:
                img_name = f"caption_{caption_counter}.{block['ext']}"
                alt_text = caption["text"]
                
                caption["used"] = True
                caption_counter += 1
                img_path = os.path.join(page_images_captions_dir, img_name)
                img_ref="./images/captions/" + img_name
                markdown_content[md_idx] = f'![{alt_text}]({img_ref})\n\n'
                cap_idx.append(markdown_content.index(alt_text+'\n'))
                del images_dict[key]                    
            else:
                img_name = f"image_{image_counter}.{block['ext']}"
                alt_text = f"Image {image_counter}"
                image_counter += 1
                img_path = os.path.join(page_images_dir, img_name)
                img_ref="./images/" + img_name
                if not image_section:
                    markdown_content.append("\n-- Page Images --\n")
                    image_section=True
                markdown_content.append(f'![{alt_text}]({img_ref})\n\n')

                # Save image

            with open(img_path, "wb") as f:
                f.write(image_bytes)

            img_end_time = time.time()
            image_times.append(img_end_time - img_start_time)

    # delete from markdown_content by image_dict keys
    idxs = list(images_dict.values())+cap_idx
    
    md_content=[l for i,l in enumerate(markdown_content) if i not in idxs]
    
    # Write final markdown file
    with open(Path(page_md_dir)/ "content.md", "w", encoding="utf-8") as f:
        f.write("".join(md_content))
    page_end_time = time.time()
    page_times.append(page_end_time - page_start_time)   

def clean_text(text):
    """Clean and normalize text"""
    text = text.replace("\n", " ").strip()
    # Remove multiple spaces
    return " ".join(text.split())

import re

def is_caption(text_block, block, prev_font_size,  style_variance=True):
    """
    Args:
        text_block: Raw text string to check.
        page: PyMuPDF page object (for font analysis).
        require_keyword: Whether to enforce "Figure"/"Table" keywords.
        style_variance: Require font style/type difference from body text.
    Returns:
        bool: True if text is likely a caption.
    """
    # 1. Check for caption keywords (case-insensitive)
    caption_keywords = r"^\s*(figure|fig\.|table|plate|image|photo|chart)\s*[0-9]*[:.-]?"
    has_keyword = re.search(caption_keywords, text_block, re.IGNORECASE) is not None
    
    # 2. Get font info for this block
    block_font = get_block_font(block)
        
    # 4. Style variance check (different font OR bold/italic)
    is_different_style = False
    if style_variance and block_font:
        is_bold = FontFlag.is_bold(block_font["flags"])
        is_italic = FontFlag.is_italic(block_font["flags"])  
        # Check bold/italic (common in captions)
        is_bold_or_italic = (   "bold" in block_font["name"].lower() or 
                                "italic" in block_font["name"].lower() or
                                is_bold or
                                is_italic
                                )
        
        is_different_style =  is_bold_or_italic or round(block_font["size"])<round(prev_font_size)
    
    return (not style_variance or is_different_style) or has_keyword

def get_block_font(block):
    """Extracts font info for a specific text block."""
    
    if not block["lines"]:
        return None
    if not block["lines"][0]["spans"]:
        return None
    
    span = block["lines"][0]["spans"][0]  # First span in first line
    return {
        "name": span["font"],
        "size": span["size"],
        "flags": span["flags"]  # Bold/italic flags (if available)
    }

def find_nearest_caption(captions, img_rect, max_distance=15):
    """Find the closest unused caption to an image"""
    closest = None
    min_dist = float('inf')
    
    for caption in captions:
        if caption["used"]:
            continue
            
        # Calculate distance between image and caption
        max_distance_ = max_distance
        dist = abs(caption["bbox"].y0 - img_rect.y1)  # Distance from image bottom to caption top
        if img_rect.y0 < caption["bbox"].y0 and img_rect.y1 > caption["bbox"].y1:
            dist = abs(img_rect.y1-caption["bbox"].y0) 
            max_distance_ = float('inf')
        
        # Prefer captions below images
        if caption["bbox"].y0 > img_rect.y1:
            dist *= 0.8  # Favor captions below images
            
        if dist < min_dist and dist < max_distance_:
            min_dist = dist
            closest = caption
    
    return closest

def is_title(text: str, threshold_length: int = 100, threshold_font_size: int = 11) -> bool:
    """
    Determines if a given text string is likely a title based on several heuristics.

    Args:
        text: The text string to evaluate.
        threshold_length: Maximum length of a title (in characters).
        threshold_font_size: Minimum font size to consider as a title (heuristic).

    Returns:
        True if the text is likely a title, False otherwise.
    """

    if not text:
        return False

    # 1. Length Check: Titles are typically short.
    if len(text) > threshold_length:
        return False
    # check is starts with uppercase
    if text[0].islower():
        return False
        
    # 2. Uppercase/Title Case Check: Titles often have capitalized words.
    uppercase_words = sum(1 for word in text.split() if word.isupper())
    titlecase_words = sum(1 for word in text.split() if word.istitle())
    total_words = len(text.split())

    if total_words > 0:
        uppercase_ratio = uppercase_words / total_words
        titlecase_ratio = titlecase_words / total_words
    else:
        uppercase_ratio = 0
        titlecase_ratio = 0

    if uppercase_ratio < 0.25 and titlecase_ratio < 0.5:
        return False

    # 3. Punctuation Check: Titles often don't end with periods.
    if text.endswith("."):
        return False

    # 4. SpaCy POS Tagging: Check for nouns and proper nouns.
    doc = nlp(text)
    noun_count = sum(1 for token in doc if token.pos_ in ["NOUN", "PROPN"])
    if noun_count < len(doc) / 2:
        return False

    # 5. Font Size Heuristic: (Not directly applicable here, but included for context)
    #    In a real PDF processing scenario, you'd check the font size.
    #    if font_size and font_size > threshold_font_size:
    #        return True

    # 6. Common Title Patterns:
    title_patterns = [
        r"^[A-Z]+[:\s]",  # All caps followed by colon or space
        r"^[A-Z][a-z]+[:\s]",  # Capitalized word followed by colon or space
        r"^[A-Z][a-z]+ [A-Z][a-z]+[:\s]",  # Two capitalized words followed by colon or space
        r"^[A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+[:\s]",  # Three capitalized words followed by colon or space
    ]
    if any(re.search(pattern, text) for pattern in title_patterns):
        return True

    return True

def extract_tables_parallel(
        pdf_path: str,
        output_dir: str,
        pages: Optional[List[int]] = None,
        max_workers: int = 4,
        flavor: str = "lattice",
        backend: str = "ghostscript",
        **kwargs
) -> Dict[int, List[str]]:
    """
    Extracts tables from multiple PDF pages in parallel.

    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save CSV files
        pages: List of 1-indexed page numbers (None=all pages)
        max_workers: Maximum parallel threads
        flavor: "lattice" or "stream"
        backend: "ghostscript" or "poppler"
        **kwargs: Additional Camelot parameters

    Returns:
        Dictionary mapping page numbers to lists of saved CSV paths

    Raises:
        FileNotFoundError: If PDF doesn't exist
    """
    # Validate PDF exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Get total pages if not specified
    if pages is None:
        with fitz.open(pdf_path) as doc:
            pages = list(range(1, len(doc) + 1))

    # Validate page numbers
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
    invalid_pages = [p for p in pages if p < 1 or p > total_pages]
    if invalid_pages:
        raise ValueError(f"Invalid page numbers: {invalid_pages}. Document has {total_pages} pages.")

    os.makedirs(output_dir, exist_ok=True)
    results = {}
    page_times = {}

    # Worker function for parallel processing
    def _process_page(page_num):
        try:
            page_start_time = time.time()
            # Suppress Camelot warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                tables = camelot.read_pdf(
                    pdf_path,
                    pages=str(page_num),
                    flavor=flavor,
                    backend=backend,
                    **kwargs
                )

            saved_files = []
            print(f"Processing page {page_num} with {len(tables)} tables...")

            for i, table in enumerate(tables, 1):
                csv_path = os.path.join(output_dir, "tables", f"page{page_num}_table{i}.csv")
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                table.df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                saved_files.append(csv_path)
            page_end_time = time.time()
            page_times[page_num] = page_end_time - page_start_time
            return page_num, saved_files
        except Exception as e:
            print(f"Error processing page {page_num}: {str(e)}")
            return page_num, []

    # Parallel execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_page, p): p for p in pages}

        for future in as_completed(futures):
            page_num, csv_files = future.result()
            results[page_num] = csv_files

    return results, page_times
filename = "GraphletAI-PropertyGraphFactory-Public.pdf"

print("Converting to markdown...")
pdf_to_markdown("./docs/"+filename, "output1/"+filename[:-4])
print("Extracting tables...")
tables_results, tables_page_times = extract_tables_parallel("./docs/" + filename, "output1/" + filename[:-4],
                                                            flavor="stream", max_workers=4)

# Update stats.json with table extraction times
stats_file_path = os.path.join("output1/" + filename[:-4], "stats.json")

if os.path.exists(stats_file_path):
    with open(stats_file_path, "r") as f:
        stats = json.load(f)

    stats["tables_page_times"] = tables_page_times
    stats["tables_total_time"] = sum(tables_page_times.values())

    

    with open(stats_file_path, "w") as f:
        json.dump(stats, f, indent=4)
else:
    print(f"Warning: stats.json not found at {stats_file_path}")