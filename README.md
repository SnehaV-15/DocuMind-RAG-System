# DocuMind – RAG-Based Document Assistant

A Retrieval-Augmented Generation (RAG) based document assistant that allows users to upload PDF documents and ask questions about their content.

DocuMind combines document processing, semantic search, vector storage, and Large Language Models (LLMs) to generate answers based on information retrieved from user-provided documents.

Instead of relying only on the general knowledge of an LLM, DocuMind retrieves relevant document passages and supplies them as context to Google Gemini to generate more relevant, document-grounded responses.

---

## Features

- **PDF Upload:** Upload PDF documents through a web interface.
- **Text Extraction:** Extracts text from PDF documents.
- **OCR Support:** Uses EasyOCR to extract text from scanned PDF pages.
- **Token-Based Chunking:** Splits extracted content into 500-token chunks with 80-token overlap.
- **Embedding Generation:** Uses Sentence Transformers to convert text chunks into vector embeddings.
- **Vector Database:** Stores document chunks and embeddings in ChromaDB.
- **Semantic Retrieval:** Retrieves the five most relevant document chunks for a user query.
- **Context-Grounded Answers:** Uses retrieved document passages as context for Gemini.
- **Source Information:** Displays retrieved chunks, source filenames, and chunk metadata.
- **RAG Comparison:** Provides a comparison between LLM responses generated with and without document retrieval.

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Backend web framework |
| HTML, CSS, JavaScript | Frontend interface |
| EasyOCR | Text extraction from scanned PDFs |
| Sentence Transformers | Text embedding generation |
| all-MiniLM-L6-v2 | Embedding model |
| ChromaDB | Vector database |
| Google Gemini API | LLM-based answer generation |

---

## System Architecture

DocuMind follows a Retrieval-Augmented Generation workflow.

### Document Processing Pipeline

1. User uploads a PDF document.
2. The application validates the uploaded PDF.
3. Text is extracted from the document.
4. EasyOCR is used when scanned pages require OCR.
5. Extracted text is stored in the `extracted_docs/` directory.
6. The text is divided into overlapping token-based chunks.
7. Sentence Transformers generates embeddings for the chunks.
8. ChromaDB stores the chunks, embeddings, and source metadata.

### Question Answering Pipeline

1. User enters a question through the web interface.
2. Sentence Transformers converts the question into an embedding.
3. ChromaDB performs semantic similarity search.
4. The five most relevant document chunks are retrieved.
5. Retrieved passages are added to the Gemini prompt as document context.
6. Gemini generates an answer based on the supplied context.
7. The application displays the answer and retrieved source information.

---

## RAG Workflow

```text
             USER UPLOADS PDF
                    |
                    v
             PDF PROCESSING
                    |
                    v
          TEXT EXTRACTION / OCR
                    |
                    v
             TEXT CHUNKING
          (500 tokens, overlap 80)
                    |
                    v
          EMBEDDING GENERATION
           (Sentence Transformers)
                    |
                    v
              CHROMADB
           (Vector Storage)
                    |
                    |
             USER QUESTION
                    |
                    v
          QUESTION EMBEDDING
                    |
                    v
          SEMANTIC RETRIEVAL
                    |
                    v
          RELEVANT DOCUMENT CHUNKS
                    |
                    v
           GEMINI LLM PROMPT
                    |
                    v
            GROUNDED ANSWER
                    |
                    v
             USER RESPONSE
```

---

## Project Structure

```text
DocuMind-RAG-System/
│
├── templates/
│   └── index.html
│
├── documents/              # Uploaded PDF documents
├── extracted_docs/         # Extracted text files
├── chroma_db/              # Persistent ChromaDB storage
│
├── app.py                  # Flask application and routes
├── config.py               # Project configuration
├── extract_documents.py    # PDF text extraction and OCR
├── ingest.py               # Text chunking and embedding storage
├── rag.py                  # Retrieval and Gemini integration
│
├── requirements.txt        # Python dependencies
├── .env.example            # Sample environment configuration
├── .gitignore              # Git ignored files
└── README.md               # Project documentation
```

**Note:** The `documents/`, `extracted_docs/`, and `chroma_db/` directories are local runtime folders. They are created or populated during application execution and are excluded from the public GitHub repository.

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/SnehaV-15/DocuMind-RAG-System.git

cd DocuMind-RAG-System
```

### 2. Create a Virtual Environment

For Windows PowerShell:

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API Key

Create a `.env` file in the project root directory using `.env.example` as a reference.

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Replace `your_api_key_here` with your actual API key.

**Important:** Never upload your `.env` file or API key to GitHub.

### 5. Run the Application

```bash
python app.py
```

Open the application in your browser:

http://127.0.0.1:5000

### 6. Upload Documents

Use the PDF upload option in the application.

The application processes the uploaded PDF, extracts its text, generates chunks and embeddings, and stores the resulting information in ChromaDB.

The application supports PDF uploads up to 25 MB.

**Alternative:** If you are preparing documents manually, place PDFs in `documents/`, run the extraction script, and then run ingestion:

```bash
python extract_documents.py

python ingest.py
```

---

## Application Modules

### 1. Document Upload and Extraction

The application accepts PDF documents and extracts their text.

For scanned documents, EasyOCR provides optical character recognition to convert page images into readable text.

### 2. Text Chunking and Embedding

Extracted text is divided into manageable chunks.

Current configuration:

| Parameter | Value |
|---|---:|
| Chunk size | 500 tokens |
| Chunk overlap | 80 tokens |
| Embedding model | all-MiniLM-L6-v2 |
| Retrieval count (Top-K) | 5 |

Overlapping chunks help preserve context between consecutive text sections.

### 3. Vector Storage

ChromaDB stores the document chunks and their corresponding embeddings.

It uses cosine distance for semantic similarity retrieval.

### 4. Semantic Retrieval

When a question is submitted, its embedding is compared with stored document embeddings.

The system retrieves the five most relevant chunks from the vector database.

### 5. Answer Generation

The retrieved chunks are supplied to Gemini as context.

The model is instructed to:
- Answer using only the supplied document context.
- Avoid inventing information.
- Indicate when the answer cannot be found in the provided documents.
- Mention source filenames when possible.

---

## Application Demonstration

DocuMind provides three main testing functionalities.

### 1. Inspect Retrieved Chunks

Displays the retrieved document passages along with:
- Source filename
- Chunk number
- Similarity distance

This helps verify whether the retrieval system finds relevant information.

### 2. Ask with RAG

Generates an answer using the retrieved document context.

The answer is grounded in the information supplied to the Gemini model.

### 3. Compare With and Without RAG

This functionality compares two responses to the same question.

**Without RAG:**
- The question is sent directly to Gemini.
- No uploaded document context is provided.
- The response is generated using the model's general knowledge.

**With RAG:**
- Relevant document chunks are retrieved from ChromaDB.
- Retrieved passages are supplied to Gemini.
- The answer is generated using the provided document context.

This comparison demonstrates how retrieval can help an LLM answer questions about information contained in specific documents.

---

## Sample Demonstration

**Question:**

"What are the names of the three HTML pages created in the Visual Studio Code Flask tutorial?"

**Expected document-specific answer:**

1. `home.html`
2. `about.html`
3. `contact.html`

The information is available on page 21 of the Flask tutorial PDF.

This question can be used to demonstrate semantic retrieval and document-grounded answering.

---

## Advantages of DocuMind

- Enables question answering over user-provided documents.
- Combines semantic search with LLM-based generation.
- Supports scanned PDF documents through OCR.
- Provides source information for retrieved passages.
- Uses persistent local vector storage.
- Allows comparison between responses with and without retrieval.
- Reduces reliance on an LLM's general knowledge for document-specific questions.

---

## Limitations

- Answer quality depends on the quality of extracted document text.
- OCR results may contain errors for low-quality scanned pages.
- Retrieval quality depends on chunking, embeddings, and document content.
- Gemini generation requires an internet connection and a valid API key.
- Gemini API usage is subject to provider rate limits.
- The system is designed for PDF documents rather than arbitrary file formats.

---

## Future Enhancements

- Support for additional document formats.
- Improved document management and deletion.
- Conversation history and multi-turn question answering.
- Advanced retrieval and reranking techniques.
- Support for multiple users.
- Improved document summarization.

---
## Screenshots

### Application Homepage
<img width="803" height="651" alt="Screenshot 2026-11-12 150540" src="https://github.com/user-attachments/assets/ea2be960-8978-40d1-91ec-27783ada6350" />


### RAG-Based Answer
<img width="863" height="802" alt="Screenshot 2026-11-12 145924" src="https://github.com/user-attachments/assets/a96ff1ac-dbde-444e-8064-16f54fbd6f28" />


### Retrieved Document Chunks
<img width="843" height="678" alt="Screenshot 2026-11-12 140813" src="https://github.com/user-attachments/assets/d8026bc8-c77b-4e8d-b2f2-e204749796c0" />


### Without-RAG Comparison
<img width="930" height="583" alt="Screenshot 2026-11-12 140740" src="https://github.com/user-attachments/assets/5a229823-0605-4bda-bcd9-d3e0c701d59e" />


## Author

**Sneha V-15**

GitHub: https://github.com/SnehaV-15

**Project:** DocuMind – RAG-Based Document Assistant

**Technologies:** Python | Flask | Sentence Transformers | ChromaDB | Google Gemini

---

*Developed as a Retrieval-Augmented Generation project to demonstrate document processing, semantic retrieval, vector databases, and context-grounded LLM responses.*
