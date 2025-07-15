# Automating Search-Based Report Generation with a Multi-Agent AI Pipeline

An multi-agent AI system that automatically generates comprehensive research reports from web sources. The system takes a high-level topic, conducts targeted research, and produces a polished report with proper citations. For a full walkthrough of this cookbook recipe, please click [here](https://inference-docs.cerebras.ai/cookbook/search-agent).

## Overview

The Search Agent follows a structured 5-phase pipeline:

1. **User Interaction**: Collects the initial topic and asks clarifying questions to understand research requirements
2. **Research & Summarization**: Generates targeted search queries, retrieves relevant articles, and creates refined summaries
3. **Report Outlining**: Synthesizes research into a structured report outline with citation placeholders
4. **Report Writing**: Converts the outline into a full-length, well-structured report
5. **Citation Management**: Formats citations and produces the final polished report

## Architecture

The system uses a modular architecture with specialized components:

- **Interactor**: Refines user topics through clarifying questions
- **Researcher**: Conducts web searches and summarizes articles using iterative refinement
- **Outliner**: Creates structured report blueprints from research summaries
- **Writer**: Transforms outlines into comprehensive reports
- **Citation Manager**: Handles proper citation formatting and final report assembly

## Prerequisites

- Python 3.8+
- Cerebras API key
- Exa API key
- Required Python packages (see requirements if available)

## Setup

1. Set your API keys as environment variables:
```bash
export CEREBRAS_API_KEY="your-cerebras-api-key"
export EXA_API_KEY="your-exa-api-key"
```

2. Install dependencies:
```bash
pip install cerebras-cloud-sdk exa-py pyyaml
```

## Usage

Run the complete pipeline:
```bash
python main.py
```

The system will:
1. Prompt you for a research topic
2. Ask clarifying questions to refine the scope
3. Conduct automated research and summarization
4. Generate a structured report outline
5. Write the full report with proper citations

## Configuration

The system uses a centralized configuration file (`config.yaml`) that allows customization of:
- Model selection for different tasks
- API parameters (max tokens, temperature)
- Research settings (number of questions, search results)
- Report specifications (word count targets)

## Output Files

The pipeline generates several intermediate and final files:
- `research_brief.json`: Structured research requirements
- `search_queries.json`: Generated search queries
- `summarized_articles.json`: Refined article summaries
- `raw_exa_results.json`: Raw search results
- `report_outline.json`: Structured report outline
- `draft_report.md`: Initial report draft
- `final_report.md`: Final report with formatted citations

## Key Features

- **Iterative Summarization**: Uses a 4-step refinement process (Reflect, Elaborate, Critique, Refine)
- **Intelligent Query Generation**: Creates targeted search queries based on user responses
- **Automated Citation Management**: Handles source tracking and proper citation formatting
- **Configurable Pipeline**: Easy customization through YAML configuration
- **Shared Client Architecture**: Optimized API usage with singleton pattern

