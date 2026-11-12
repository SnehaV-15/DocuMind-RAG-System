# DocuMind – RAG-Based Document Assistant

DocuMind is a Retrieval-Augmented Generation (RAG) based document assistant that allows users to ask questions about their uploaded PDF documents.

It extracts text from PDFs, including scanned documents using OCR, divides the extracted content into overlapping chunks, generates embeddings using Sentence Transformers, and stores them in ChromaDB.

When a user asks a question, DocuMind retrieves the most relevant document passages and provides them as context to the Gemini language model to generate a grounded answer.

## Features

- **PDF Processing:** Extracts text from PDFs and uses EasyOCR for scanned pages.
- **Token-Based Chunking:** Splits documents into 500-token chunks with 80-token overlap.
- **Local Embeddings:** Uses Sentence Transformers (`all-MiniLM-L6-v2`).
- **Vector Database:** Stores embeddings in a persistent ChromaDB collection.
- **Semantic Retrieval:** Retrieves the five most relevant chunks for a question.
- **Context-Grounded Answers:** Uses retrieved passages to generate answers through Gemini.
- **Source Information:** Displays retrieved document names and chunk details.
- **RAG Comparison:** Compares answers generated with and without document retrieval.

## Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Framework | Flask |
| PDF Processing | PDF extraction and EasyOCR |
| Embedding Model | Sentence Transformers |
| Vector Database | ChromaDB |
| Language Model | Google Gemini |
| Frontend | HTML, CSS, JavaScript |

## System Architecture

The application follows this workflow:

1. User uploads a PDF document.
2. Text is extracted from the PDF.
3. OCR is used when scanned pages require text recognition.
4. Extracted text is divided into overlapping chunks.
5. Sentence Transformers generates vector embeddings.
6. ChromaDB stores the chunks and embeddings.
7. User submits a question.
8. The question is converted into an embedding.
9. ChromaDB retrieves the most relevant document chunks.
10. Retrieved context is passed to Gemini.
11. Gemini generates an answer grounded in the supplied document context.

## Project Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd DocuMind-RAG-System
```

### 2. Create a virtual environment

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your Gemini API key.

Example:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Never upload your actual `.env` file or API key to GitHub.

### 5. Add documents

Place your PDF documents inside the `documents/` directory.

Use a substantive document collection equivalent to at least 10–20 pages.

### 6. Extract document text

```bash
python extract_documents.py
```

The extracted text is stored in `extracted_docs/`.

Check the extracted files to ensure that the text is readable.

### 7. Generate chunks and embeddings

```bash
python ingest.py
```

This process:
- Splits extracted text into chunks.
- Generates embeddings.
- Stores document chunks and embeddings in ChromaDB.

### 8. Run the application

```bash
python app.py
```

Open the application in your browser:

http://127.0.0.1:5000

## Application Demonstration

DocuMind provides three important ways to test the RAG pipeline.

**1. Inspect Retrieved Chunks**

Displays the most relevant document passages retrieved from ChromaDB, including source filenames, chunk numbers, and retrieval distances.

**2. Ask with RAG**

Generates an answer using retrieved document context. The model is instructed to answer only from the supplied context.

**3. Compare With and Without RAG**

Compares two responses to the same question:

- Without RAG: Gemini answers using its general knowledge without uploaded document context.
- With RAG: Gemini answers using relevant passages retrieved from ChromaDB.

### Example Demonstration Question

Question:

"What are the names of the three HTML pages created in the Visual Studio Code Flask tutorial?"

Expected document-specific answer:

- `home.html`
- `about.html`
- `contact.html`

The relevant information is available in the Flask tutorial document, page 21.

Use this question to demonstrate retrieval and grounded answering. Record the actual outputs of both comparison modes before claiming a successful comparison.

## Project Structure

```text
DocuMind-RAG-System/
│
├── documents/             # Uploaded PDF documents
├── extracted_docs/        # Extracted text files
├── chroma_db/             # Persistent vector database
│
├── templates/
│   └── index.html         # Web application interface
│
├── app.py                 # Flask application and routes
├── config.py              # Project configuration
├── extract_documents.py   # PDF text extraction and OCR
├── ingest.py               # Chunking and embedding generation
├── rag.py                  # Retrieval and Gemini integration
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Important Notes

- Sentence Transformers generates embeddings locally.
- ChromaDB stores the vector database locally.
- Gemini API is used for language generation and requires an API key.
- Initial setup may download embedding and OCR models.
- OCR accuracy depends on document quality and scan resolution.
- Gemini API usage is subject to the provider's rate limits.
- The application is designed to answer from retrieved document context and should indicate when the required information cannot be found.

## Future Enhancements

- Support additional document formats.
- Improve document management and deletion.
- Add conversation history.
- Implement more advanced retrieval techniques.
- Add support for multiple users.

## Author

Developed as a Retrieval-Augmented Generation project using Python, Flask, Sentence Transformers, ChromaDB, and Google Gemini.
