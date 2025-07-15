# Implementing Gist Memory: Summarizing and Searching Long Documents with a ReadAgent

An AI system that enables efficient question-answering on long documents by using [Gist memory](https://arxiv.org/abs/2402.09727), a technique developed by Google DeepMind. The agent processes lengthy papers into digestible "gists" and intelligently retrieves specific sections when answering questions, inspired by how humans naturally skim and recall information.

## Overview

The Gist Memory Agent follows a structured pipeline:

1. **Document Ingestion**: Converts ArXiv papers from PDF to HTML format for structured parsing
2. **Intelligent Pagination**: Automatically identifies natural break points in documents (scene transitions, argument endings)
3. **Hierarchical Summarization**: Creates compressed "gist" representations of each page while preserving key information
4. **Selective Memory Retrieval**: When answering questions, identifies which pages need detailed re-examination
5. **Context-Aware Response**: Expands relevant gists back to full text for accurate answer generation

## Architecture

The system uses a modular architecture with specialized components:

- **GistAgent**: Core orchestrator that manages document processing and question-answering
- **ArXiv Parser**: Handles conversion of ArXiv papers to structured HTML via ar5iv service
- **Pagination Engine**: Uses LLM to find natural document break points for optimal chunking
- **Gist Memory**: Creates and manages hierarchical summaries of document sections
- **Selective Retrieval**: Intelligently determines which sections to expand for detailed analysis

## Prerequisites

- Python 3.8+
- Cerebras API key
- Required Python packages (see requirements if available)

## Setup

1. Set your API key as environment variable:
```bash
export CEREBRAS_API_KEY="your-cerebras-api-key"
```

2. Install dependencies:
```bash
pip install cerebras-cloud-sdk requests beautifulsoup4
```

## Usage

Run the agent:
```bash
python gist_agent.py
```

The system will:
1. Prompt for an ArXiv paper URL (or use default Gist Memory paper)
2. Process the document into paginated gists
3. Enter interactive Q&A mode where you can ask questions about the paper
4. Display performance metrics after each operation

## Configuration

The agent uses configurable parameters:
- Model selection (default: llama-3.3-70b)
- Word limits for pagination (600 words per page)
- Start threshold for break point detection (280 words)
- Maximum pages for retrieval during Q&A (1-6 pages)

