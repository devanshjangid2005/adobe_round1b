```markdown
# Adobe Hackathon: Round 1A + 1B Offline Pipeline

This repository implements a fully offline, CPU‑only pipeline for:

1. **Round 1A**: Extracting document structure (title + H1–H3 headings with page numbers) from PDFs via a local LLM (`allenai/unifiedqa-t5-small`).
2. **Round 1B**: Persona‑driven retrieval of the most relevant sections using a RAG approach (MiniLM + FAISS + TF–IDF) and batch summarization (`sshleifer/distilbart-cnn-6-6`).

---

## 📂 Repository Structure

```

adobe\_round1b/
├── README.md
├── main.py
├── utils.py
├── round1a\_extractor.py
├── preprocess.py
├── embed\_index.py
├── retrieve\_rank.py
├── summarize.py
├── requirements.txt
├── input/                  ← place your .pdf files here
│   └── \*.pdf
└── output/                 ← generated JSON will appear here

````

---

## ⚙️ Prerequisites

- Python 3.8+  
- 2 GB free disk (for model caches & indexes)  
- Windows/Linux/macOS terminal

---

## 📥 Installation

1. **Create & activate** a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # or .\venv\Scripts\Activate.ps1 on Windows
````

2. **Install** dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   `requirements.txt` includes:

   ```
   protobuf
   tiktoken
   sentencepiece
   PyMuPDF
   transformers>=4.33.2
   torch>=1.13.1
   sentence-transformers
   faiss-cpu
   scikit-learn
   scipy
   numpy
   ```

---

## ⬇️ Model Pre‑caching (ONE‑TIME, ONLINE)

Before you run fully offline, **download** and cache the required models:

```bash
python - <<'EOF'
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from sentence_transformers import SentenceTransformer

# Round 1A extractor
AutoTokenizer.from_pretrained("allenai/unifiedqa-t5-small")
AutoModelForSeq2SeqLM.from_pretrained("allenai/unifiedqa-t5-small")

# RAG indexer
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Summarizer
pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
EOF
```

This caches:

* `allenai/unifiedqa-t5-small`
* `sentence-transformers/all-MiniLM-L6-v2`
* `sshleifer/distilbart-cnn-6-6`

---

## 🚀 Running the Pipeline (OFFLINE)

Once cached, disable internet and run **end‑to‑end**:

```bash
python main.py \
  --persona "Travel Planner" \
  --job "Plan a trip of 4 days for a group of 10 college friends" \
  --input_dir ./input \
  --output_file ./output/challenge1b_output.json
```

* `--persona`: describes the target reader
* `--job`: describes the use‑case/query
* `--input_dir`: folder with your `.pdf` files
* `--output_file`: path for the final JSON

---

## 📋 Input & Output

* **Input**:

  * Place your PDFs in `input/`.
  * Round 1A JSON outlines are auto‑generated next to each PDF.

* **Output**:

  * Intermediate files:

    * `chunks.pkl`, `faiss.index`, `meta.json`, `tfidf.pkl`, `tfidf.npz`
  * **Final**: `output/challenge1b_output.json` containing:

    ```jsonc
    {
      "metadata": { "documents": [...], "persona": "...", "job": "...", "timestamp": "..." },
      "extracted_sections": [
        { "document":"...pdf", "page":2, "section_title":"...", "score":0.93 },
        …
      ],
      "subsection_analysis": [
        { "doc_id":"...pdf", "page":2, "section_title":"…", "refined_text":"…" },
        …
      ]
    }
    ```

---

## 🔧 Module Summaries

* **`round1a_extractor.py`**
  Chunk‑based LLM extraction of title + headings (local UnifiedQA).

* **`preprocess.py`**
  Reads the JSON outlines + PDFs → tokenized text chunks.

* **`embed_index.py`**
  Builds a FAISS index of MiniLM embeddings + precomputes TF–IDF.

* **`retrieve_rank.py`**
  Embeds the persona+job query → retrieves top‑K sections by hybrid cosine+TF–IDF.

* **`summarize.py`**
  Batch summarizes top sections with DistilBART.

* **`main.py`**
  Orchestrates the full Round 1A→1B pipeline.

---

## 🛠 Troubleshooting

* **“Cannot find…cache and outgoing traffic disabled”**
  Ensure you ran the **Model Pre‑caching** step online.

* **Token limit warnings**
  All chunks are truncated to ≤ 200 tokens; warnings can be ignored.

* **Empty `chunks.pkl`**
  Verify your Round 1A JSONs contain non‑empty `headings`.

---

## 📄 License

This code is provided under the MIT License. See [LICENSE](LICENSE) for details.

```
```
