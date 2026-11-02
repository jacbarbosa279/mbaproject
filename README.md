# Georeferenced Crime Sentiment Analysis

This project processes vehicle-theft records from São Paulo, generates social media
alerts, analyzes their sentiment, and creates an interactive crime map and a sentiment
chart.

Developed as part of the **MBA in Artificial Intelligence and Big Data** at the
**Institute of Mathematics and Computer Sciences, University of São Paulo (ICMC/USP)**.

## How it works

The main entry point, `main_script_app_sentimento.py`, reads the
`AMOSTRAGEM` sheet in `data/raw/VeiculosSubtraidos_2024.xlsx` and processes each
record:

1. Generates a vehicle-theft alert and a positive policing message.
2. Uses NLTK VADER to analyze both messages.
3. Chooses the policing-message prompt based on whether the crime alert's VADER
   compound score is negative.
4. Adds the incident to an interactive Folium map and includes both sentiment
   scores in an HTML chart.

The `src/` package contains reusable modules for data loading and validation,
message generation, VADER analysis, and visualization. The main script remains the
executable entry point.

## Language model

When an API key is configured, messages are generated through OpenRouter using
`google/gemma-4-26b-a4b-it:free`. This replaces the original script's
`LLaMA-3.2-3B-Instruct` model because that LLM became unavailable. If the API key
is missing or an API request fails, the script reports the issue and uses local
fallback messages instead.

Set either `OPENROUTER_API_KEY` or `OPENAI_API_KEY` before running to enable API
generation. For example, in PowerShell:

```powershell
$env:OPENROUTER_API_KEY = "your-api-key"
```

## Requirements and running

Use Python 3.10 or later. Install the dependencies and run the main script from
the repository root:

```powershell
python -m pip install -r requirements.txt
python main_script_app_sentimento.py
```

The script downloads the NLTK `vader_lexicon` resource if needed. The input
spreadsheet must be present at `data/raw/VeiculosSubtraidos_2024.xlsx`.

## Generated files

- `output/grafico_sentimentos.html` — sentiment chart with an embedded image.
- `output/mapa_crimes.html` — interactive map with crime markers.
- `data/processed/mensagens_geradas.txt` — generated messages and sentiment scores.

The `src/` modules use these same output locations by default.

## Solution Architecture

The following diagram illustrates the data flow and components of the analysis and alert generation script:

```mermaid
flowchart TD
    subgraph Input ["Data Input"]
        Excel["data/raw/VeiculosSubtraidos_2024.xlsx"]
    end

    subgraph Config ["Authentication & Providers"]
        ENV{"OPENROUTER_API_KEY /<br/>OPENAI_API_KEY"}
        OpenRouter["OpenRouter API<br/>(LLM: Gemma 4 / Llama)"]
        Fallback["Local Generator<br/>(Offline Fallback)"]
    end

    subgraph Processing ["Processing & Analysis"]
        Iterate["Line-by-Line Iteration<br/>(Pandas DataFrame)"]
        Geocoding["Coordinates Extraction<br/>(Lat/Long, Neighborhood, Date/Time)"]
        
        GenPostRoubo["Robbery Alert Generation"]
        NLTK1["NLTK VADER<br/>(Sentiment Analysis #1)"]
        
        PromptLogic{"Compound Score < 0?"}
        PromptPositivo["Prompt: Praise/Policing"]
        PromptNeutro["Prompt: Police Presence"]
        
        GenPostPolicia["Police Message Generation"]
        NLTK2["NLTK VADER<br/>(Sentiment Analysis #2)"]
    end

    subgraph Output ["Generated Artifacts"]
        TXT["data/processed/mensagens_geradas.txt<br/>(Posts + Sentiments)"]
        Mapa["output/mapa_crimes.html<br/>(Folium Map / Markers)"]
        Grafico["output/grafico_sentimentos.html<br/>(Matplotlib / Base64 HTML)"]
    end

    %% Input Relations
    Excel --> Iterate

    %% Config/LLM Relations
    ENV -- Present --> OpenRouter
    ENV -- Missing / Error --> Fallback
    
    OpenRouter --> GenPostRoubo
    Fallback --> GenPostRoubo
    
    OpenRouter --> GenPostPolicia
    Fallback --> GenPostPolicia

    %% Main Flow
    Iterate --> Geocoding
    Geocoding --> Mapa
    Iterate --> GenPostRoubo
    
    GenPostRoubo --> NLTK1
    NLTK1 --> PromptLogic
    
    PromptLogic -- Yes --> PromptPositivo
    PromptLogic -- No --> PromptNeutro
    
    PromptPositivo --> GenPostPolicia
    PromptNeutro --> GenPostPolicia
    
    GenPostPolicia --> NLTK2
    
    %% Gravação e Saída
    NLTK1 --> TXT
    NLTK2 --> TXT
    NLTK1 & NLTK2 --> Grafico
