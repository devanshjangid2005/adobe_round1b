```markdown
# Adobe Hackathon: Round 1A + 1B Offline Pipeline

This repository implements a fully offline, CPU‑only pipeline for:

1. **Round 1A**: Extracting document structure (title + H1–H3 headings with page numbers) from PDFs using a heuristic‑based parser.
2. **Round 1B**: Persona‑driven semantic retrieval of the most relevant sections using a SentenceTransformer (MiniLM) model for ranking.

---

## 📂 Repository Structure

```

adobe\_round1b/
├── README.md
├── round1b\_solution.py
├── requirements.txt
├── input/                  ← place your .pdf files here
│   └── \*.pdf
├── input/challenge1b\_input.json  ← JSON specifying persona, job, and input docs
└── output/                 ← generated JSON will appear here

````

---

## ⚙️ Prerequisites

- Python 3.8+ OR Docker
- 2 GB free disk (for model caches & indexes)
- Windows/Linux/macOS terminal

---

## 🐳 Docker Setup

You can run this pipeline entirely in Docker (no need to install Python locally).

### 1️⃣ Build the Docker image
```bash
docker build -t adobe-hackathon-solution .
````

This will:

* Download the MiniLM model (`all-MiniLM-L6-v2`) in a builder stage.
* Copy it into the final container.
* Install all required dependencies.

---

### 2️⃣ Run the container

Make sure your PDFs and input JSON are in `input/`. Then:

```bash
docker run --rm \
  -v ${PWD}/input:/app/input \
  -v ${PWD}/output:/app/output \
  adobe-hackathon-solution
```

This mounts your `input/` and `output/` folders into the container so results are stored locally.

The container will process:

* PDFs from `input/`
* `input/challenge1b_input.json`
* Write results to `output/challenge1b_output.json`

---

## 🚀 Running Locally (Without Docker)

If you prefer running it directly:

1. **Create & activate** a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # or .\venv\Scripts\Activate.ps1 on Windows
   ```

2. **Install** dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run**:

   ```bash
   python round1b_solution.py
   ```

---

## 🧠 Approach Explained

### `round1b_solution.py` Workflow

1. **Configuration:**

   * Defines paths for input PDFs, the challenge JSON input file, the output file, and the embedding model (`all-MiniLM-L6-v2`).

2. **PDF Parsing (Section & Subsection Extraction):**

   * Uses **PyMuPDF** to read PDFs.
   * Collects font sizes across all pages to determine a **heading size threshold**.
   * Iterates through blocks of text:

     * If a block has a large font size and is short → treated as a **section heading**.
     * Text blocks under it are grouped as **subsection content**.
   * Returns a structured list of `{section_title, subsection_text, page_number}`.

3. **Semantic Search & Ranking:**

   * Loads the MiniLM SentenceTransformer.
   * Reads persona and job context from `challenge1b_input.json`.
   * Constructs a query: `"<persona>: <job_to_be_done>"`.
   * Embeds both query and document sections using MiniLM.
   * Ranks sections and subsections by **cosine similarity**.

4. **Top‑K Selection:**

   * Picks the **top 5 sections** and **top 5 subsections** most relevant to the persona’s query.

5. **Output JSON:**

   * Saves a JSON file with:

     * `metadata` (persona, job, timestamp).
     * `extracted_sections` (titles, pages, ranks).
     * `subsection_analysis` (refined text chunks).

---

## 📋 Input & Output Example

### Input (`input/challenge1b_input.json`)

```json
{
  "persona": { "role": "Travel Planner" },
  "job_to_be_done": { "task": "Plan a 4-day trip for 10 friends" },
  "documents": [
    { "filename": "guide.pdf" },
    { "filename": "itinerary.pdf" }
  ]
}
```

### Output (`output/challenge1b_output.json`)

```json
{
  "metadata": { "input_documents": ["guide.pdf"], "persona": "Travel Planner", "job_to_be_done": "Plan a 4-day trip for 10 friends", "processing_timestamp": "..." },
  "extracted_sections": [
    { "document": "guide.pdf", "section_title": "Best Destinations", "importance_rank": 1, "page_number": 2 }
  ],
  "subsection_analysis": [
    { "document": "guide.pdf", "refined_text": "Detailed itinerary...", "page_number": 2 }
  ]
}
```

---

## 🛠 Troubleshooting

* **Slow Docker build:** Ensure Docker DNS is set in `daemon.json`:

  ```json
  {
    "dns": ["8.8.8.8", "8.8.4.4"]
  }
  ```

  Restart Docker Desktop afterward.

* **Timeouts during pip install:** Increase pip timeout:

  ```dockerfile
  RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
  ```

* **Empty sections in output:** Verify PDFs have extractable text (not scanned images).

---

## 📄 License

This project is licensed under the MIT License.

```

