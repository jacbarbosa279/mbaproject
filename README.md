# Georeferenced Sentiment Analysis for Urban Mobility Risk Assessment

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Institution](https://img.shields.io/badge/USP-ICMC-gold)](https://www.icmc.usp.br/)

This repository contains the research framework, analytical pipelines, and visualization tools for aggregating georeferenced crime data and user comments to compute dynamic risk indicators for urban mobility applications (e.g., Waze, Google Maps). 

Developed as part of the **MBA in Artificial Intelligence and Big Data** at the **Institute of Mathematics and Computer Sciences, University of São Paulo (ICMC/USP)**.

---

## Abstract

Urban mobility applications extensively utilize real-time traffic data, yet often omit critical public safety indicators due to concerns over persistent regional stigmatization. This project proposes a dynamic risk identification system that processes georeferenced incident reports, evaluates textual sentiment via Natural Language Processing (NLP) and Large Language Models (LLMs), and maps risk regions with time-bound alert expirations.

### Key Contributions
- **LLM Synthetic Alert Generation**: Integrates `LLaMA-3.2-3B-Instruct` (via OpenRouter API) to generate contextualized social media posts based on official public safety datasets from São Paulo.
- **Sentiment Analysis Benchmarking**: Evaluates and compares two NLP classification paradigms:
  - **VADER** (Valence Aware Dictionary and sEntiment Reasoner): Lexicon-based approach optimized for real-time, short-text informal alerts without requiring model training.
  - **Naive Bayes Classifier**: Probabilistic approach trained on structured textual data for baseline classification.
- **Geospatial & Interactive Mapping**: Leverages `Folium` to generate interactive heatmaps and point-of-interest markers displaying localized criminal severity, timestamps, and sentiment intensity.

---

## System Architecture

```mermaid
graph TD
    A[Public Crime Dataset / SSP-SP] --> B[Data Preprocessing & Validation]
    B --> C[LLM Generation: LLaMA-3.2-3B-Instruct]
    C --> D[Synthetic Alert Posts]
    D --> E1[VADER Lexicon Analyzer]
    D --> E2[Naive Bayes Classifier]
    E1 --> F[Interactive Map Rendering / Folium]
    E2 --> F
    E1 --> G[Sentiment Score Distribution / Matplotlib]
    E2 --> G

