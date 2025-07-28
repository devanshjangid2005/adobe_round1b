import json
import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util
import torch
from datetime import datetime

# --- 1. Configuration ---
PDF_DIRECTORY = 'input'
R1B_INPUT_FILE = 'input/challenge1b_input.json'
MODEL_NAME = 'all-MiniLM-L6-v2'
OUTPUT_FILE_NAME = 'output/challenge1b_output.json'

# --- 2. PDF Processing ---

def extract_and_structure_pdf(pdf_path: str):
    """
    Extracts text and structures it into sections and subsections.
    - Sections are identified by font size (heuristic).
    - Subsections are the text blocks under each section title.
    """
    doc_sections = []
    try:
        doc = fitz.open(pdf_path)
        
        # --- Heuristic for finding heading sizes ---
        font_sizes = {}
        for page in doc:
            for block in page.get_text("dict")["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            size = round(span["size"])
                            font_sizes[size] = font_sizes.get(size, 0) + 1
        
        sorted_sizes = sorted(font_sizes.keys(), reverse=True)
        
        # Define a threshold for what constitutes a heading.
        heading_threshold_size = sorted_sizes[min(1, len(sorted_sizes)-1)] if sorted_sizes else 12

        current_section_title = "Introduction" # Default title for text before the first heading
        current_page_number = 1
        current_text_chunks = []

        for page_num, page in enumerate(doc, 1):
            blocks = sorted(page.get_text("dict")["blocks"], key=lambda b: b['bbox'][1])
            for block in blocks:
                if "lines" not in block:
                    continue
                
                block_text = " ".join([span["text"] for line in block["lines"] for span in line["spans"]]).strip()
                if not block_text:
                    continue
                
                # Check if the block is likely a heading based on font size.
                span_sizes = [round(s['size']) for l in block['lines'] for s in l['spans']]
                is_heading = any(s >= heading_threshold_size for s in span_sizes) if span_sizes else False

                if is_heading and len(block_text.split()) < 20: # Headings are usually short
                    if current_section_title and current_text_chunks:
                        doc_sections.append({
                            "section_title": current_section_title,
                            "subsection_text": " ".join(current_text_chunks),
                            "page_number": current_page_number
                        })
                    
                    current_section_title = block_text
                    current_page_number = page_num
                    current_text_chunks = []
                else:
                    current_text_chunks.append(block_text)

        if current_section_title and current_text_chunks:
            doc_sections.append({
                "section_title": current_section_title,
                "subsection_text": " ".join(current_text_chunks),
                "page_number": current_page_number
            })
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")

    return doc_sections

# --- 3. Semantic Search & Ranking ---

def rank_items(model, query, items, text_key):
    """Generic function to rank items based on semantic similarity."""
    if not items:
        return []
    
    texts_to_embed = [item[text_key] for item in items]
    
    query_embedding = model.encode(query, convert_to_tensor=True, device='cpu')
    item_embeddings = model.encode(texts_to_embed, convert_to_tensor=True, device='cpu')
    
    cosine_scores = util.cos_sim(query_embedding, item_embeddings)[0]
    
    for item, score in zip(items, cosine_scores):
        item['score'] = score.item()
        
    return sorted(items, key=lambda x: x['score'], reverse=True)

# --- 4. Main Execution ---

if __name__ == "__main__":
    # --- Part 1: Load inputs and model ---
    print("🚀 Initializing solution...")
    model = SentenceTransformer(MODEL_NAME)
    
    with open(R1B_INPUT_FILE, 'r', encoding='utf-8') as f:
        r1b_data = json.load(f)

    persona = r1b_data.get("persona", {}).get("role", "")
    job_to_be_done = r1b_data.get("job_to_be_done", {}).get("task", "")
    search_query = f"{persona}: {job_to_be_done}"

    pdf_files = [doc["filename"] for doc in r1b_data.get("documents", [])]

    # --- Part 2: Process all PDFs ---
    all_sections = []
    print("\n📄 Processing PDFs...")
    for pdf_file in pdf_files:
        pdf_path = os.path.join(PDF_DIRECTORY, pdf_file)
        if os.path.exists(pdf_path):
            print(f"   - Reading {pdf_file}")
            extracted_data = extract_and_structure_pdf(pdf_path)
            for section in extracted_data:
                section['document'] = pdf_file
                all_sections.append(section)
        else:
            print(f"   - ⚠️ Warning: PDF file not found at {pdf_path}")
    
    # --- Part 3: Rank sections and subsections ---
    print("\n🧠 Ranking extracted content...")
    ranked_titles = rank_items(model, search_query, all_sections, 'section_title')
    ranked_subsections = rank_items(model, search_query, all_sections, 'subsection_text')

    # --- Part 4: Format the final JSON output ---
    final_output = {
        "metadata": {
            "input_documents": pdf_files,
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [
            {
                "document": section["document"],
                "section_title": section["section_title"],
                "importance_rank": i + 1,
                "page_number": section["page_number"]
            } for i, section in enumerate(ranked_titles[:5]) # Top 5 sections
        ],
        "subsection_analysis": [
            {
                "document": section["document"],
                "refined_text": section["subsection_text"],
                "page_number": section["page_number"]
            } for section in ranked_subsections[:5] # Top 5 subsections
        ]
    }

    # --- Part 5: Save the result to a file ---
    print(f"\n💾 Saving final output to {OUTPUT_FILE_NAME}...")
    with open(OUTPUT_FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)
    
    print("✅ Done!")



