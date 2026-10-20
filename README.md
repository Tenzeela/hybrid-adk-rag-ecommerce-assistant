# Hybrid Agentic AI E-commerce Assistant

A multi-agent e-commerce assistant built with Google ADK, Groq, PostgreSQL, ChromaDB, and Retrieval-Augmented Generation (RAG).

## Features

- **Supervisor Agent:** Routes user queries to specialized agents.
- **Product Specialist:** Searches PostgreSQL for product prices and inventory.
- **Policy Specialist:** Retrieves information from store policies and PDF documents using RAG.
- **Customer Memory:** Saves and retrieves customer preferences across sessions.
- **Hybrid Architecture:** Combines structured database queries with vector-based knowledge retrieval.

## Tech Stack

- Python 3.11
- Google Agent Development Kit (ADK)
- Groq + LiteLLM
- PostgreSQL + SQLAlchemy
- ChromaDB
- RAG and PDF processing
- Docker Compose

## Architecture

User → Supervisor Agent → Specialist Agents / Memory Tools → PostgreSQL or ChromaDB → Response

## Setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install the project dependencies.
4. Configure the required environment variables in a local `.env` file.
5. Start PostgreSQL using Docker Compose.
6. Initialize the database and load the knowledge documents.
7. Run the ADK web interface.

## Environment Variables

Configure the following variables in your local `.env` file:

- `GROQ_API_KEY`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Never commit your `.env` file or credentials.

## Project Status

Implemented and tested: product search, document-based retrieval, supervisor routing, and PostgreSQL-backed customer memory across ADK sessions.

**Note:** Customer memory currently uses a fixed demo customer ID. Authentication and secure multi-customer isolation are future improvements.