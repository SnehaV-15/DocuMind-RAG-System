
"""DocuMind Flask application."""

from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from config import DOCUMENTS_DIR, EXTRACTED_DIR
from extract_documents import extract_pdf
from ingest import ingest_documents
from rag import (
    answer_with_rag,
    answer_without_rag,
    retrieve,
    refresh_collection
)

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf"}


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "PDF is too large. Maximum upload size is 25 MB."
    }), 413


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_document():

    uploaded = request.files.get("file")

    if uploaded is None or not uploaded.filename:
        return jsonify({
            "error": "Please select a PDF file."
        }), 400

    original_name = secure_filename(uploaded.filename)

    if Path(original_name).suffix.lower() not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": "Only PDF files are supported."
        }), 400

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    unique_name = (
        f"{Path(original_name).stem}_{uuid4().hex[:8]}.pdf"
    )

    pdf_path = DOCUMENTS_DIR / unique_name
    extracted_path = (
        EXTRACTED_DIR / f"{Path(unique_name).stem}.txt"
    )

    uploaded.save(pdf_path)

    try:
        # Basic PDF file validation
        with pdf_path.open("rb") as file:
            if file.read(5) != b"%PDF-":
                raise ValueError("The uploaded file is not a valid PDF.")

        # Extract selectable text and OCR scanned pages
        print(f"Processing uploaded PDF: {original_name}")

        extracted_text = extract_pdf(pdf_path)

        if len(extracted_text.strip()) < 50:
            raise ValueError(
                "Not enough readable text was found in this PDF."
            )

        extracted_path.write_text(
            extracted_text,
            encoding="utf-8"
        )

        # Add document chunks and embeddings to ChromaDB
        total_chunks = ingest_documents()

        # Refresh cached collection
        refresh_collection()

        return jsonify({
            "message": f"{original_name} uploaded and indexed successfully.",
            "chunks": total_chunks
        }), 200

    except Exception as exc:

        # Remove failed upload files, but preserve existing documents
        pdf_path.unlink(missing_ok=True)
        extracted_path.unlink(missing_ok=True)

        app.logger.exception("PDF upload failed")

        return jsonify({
            "error": str(exc)
        }), 500


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    try:
        result = answer_with_rag(question)
        return jsonify(result)

    except Exception as exc:
        app.logger.exception("RAG answer failed")

        return jsonify({
            "error": str(exc)
        }), 500


@app.route("/retrieve", methods=["POST"])
def retrieve_only():

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    try:
        chunks = retrieve(question)

        return jsonify({
            "chunks": chunks
        })

    except Exception as exc:
        app.logger.exception("Document retrieval failed")

        return jsonify({
            "error": str(exc)
        }), 500


@app.route("/compare", methods=["POST"])
def compare():

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    result = {
        "without_rag": None,
        "with_rag": None,
        "sources": [],
        "errors": {}
    }

    # Generate baseline answer independently
    try:
        result["without_rag"] = answer_without_rag(question)

    except Exception as exc:
        app.logger.exception("Without-RAG generation failed")
        result["errors"]["without_rag"] = str(exc)

    # Generate RAG answer independently
    try:
        rag_result = answer_with_rag(question)

        result["with_rag"] = rag_result["answer"]
        result["sources"] = rag_result["sources"]

    except Exception as exc:
        app.logger.exception("With-RAG generation failed")
        result["errors"]["with_rag"] = str(exc)

    # Return both results, even if one generation fails
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)
