from pathlib import Path

import chromadb
import pymupdf

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
PDF_DIR = KNOWLEDGE_DIR / "pdfs"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"

# Persistent ChromaDB client
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name="ecommerce_knowledge"
)


def load_documents():
    """Load TXT files and extract text from PDF pages."""
    documents = []

    # Load existing TXT files
    for file_path in sorted(KNOWLEDGE_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if text:
            documents.append({
                "source": file_path.name,
                "page": 0,
                "text": text,
            })

    # Load PDF files from knowledge/pdfs/
    if PDF_DIR.exists():
        for file_path in sorted(PDF_DIR.glob("*.pdf")):
            try:
                with pymupdf.open(file_path) as pdf:
                    for page_number, page in enumerate(pdf, start=1):
                        text = page.get_text().strip()

                        if text:
                            documents.append({
                                "source": file_path.name,
                                "page": page_number,
                                "text": text,
                            })

                print(f"Loaded PDF: {file_path.name}")

            except Exception as error:
                print(f"Error reading {file_path.name}: {error}")

    return documents


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """Split text into overlapping character-based chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def index_knowledge():
    """Index TXT documents and PDF pages in ChromaDB."""
    documents = load_documents()

    if not documents:
        print("No knowledge documents found.")
        return

    ids = []
    texts = []
    metadatas = []

    for document in documents:
        chunks = chunk_text(document["text"])

        for index, chunk in enumerate(chunks):
            source = document["source"]
            page = document["page"]

            ids.append(f"{source}_page{page}_chunk{index}")
            texts.append(chunk)

            metadatas.append({
                "source": source,
                "page": page,
                "chunk": index,
            })

    if not texts:
        print("No text chunks found to index.")
        return

    # Replace previous indexed records
    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Document pages/files loaded: {len(documents)}")
    print(f"Chunks indexed: {len(texts)}")
    print(f"Total chunks in ChromaDB: {collection.count()}")


def search_knowledge(query: str, n_results: int = 2):
    """Retrieve relevant knowledge chunks for a question."""
    if not query or not query.strip():
        return []

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    result = collection.query(
        query_texts=[query],
        n_results=min(n_results, total_chunks),
    )

    matches = []

    for text, metadata, distance in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        matches.append({
            "text": text,
            "source": metadata["source"],
            "page": metadata["page"],
            "distance": distance,
        })

    return matches


if __name__ == "__main__":
    index_knowledge()

    question = "How long do customers have to return a product?"
    results = search_knowledge(question)

    print(f"\nQuestion: {question}")
    print("\nRetrieved knowledge:")

    for result in results:
        print(f"\nSource: {result['source']}")
        print(f"Page: {result['page']}")
        print(result["text"])
        print(f"Distance: {result['distance']:.4f}")