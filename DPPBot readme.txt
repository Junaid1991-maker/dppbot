# DPPBot — EU Digital Product Passport Compliance AI Agent

![Python](https://img.shields.io/badge/Python-3.10-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![Claude](https://img.shields.io/badge/Claude-AI-purple)

> Project 2 of the AI Engineering Portfolio by Junaid Iqbal — iamjunaidiqbal.com

---

## What is DPPBot?

DPPBot is an AI agent that helps Pakistani textile exporters understand and comply with EU Digital Product Passport (DPP) regulations. By 2027, every textile product entering the EU market must have a DPP — a digital record of material composition, chemical substances, carbon footprint, and supplier chain. DPPBot answers compliance questions, identifies certification gaps, generates action plans, and scores readiness from 0 to 100.

---

## The Problem It Solves

Pakistan exports billions of dollars of textiles to Europe every year. Most exporters are running on thin margins and now face complex EU regulations — ESPR Article 7, REACH chemical testing, ZDHC certification, OEKO-TEX standards — with no clear guidance in their language or context. DPPBot gives them a practical, Pakistan-specific compliance assistant.

---

## Live Demo

Ask DPPBot questions like:
- "I export denim to Germany. What certifications do I need by 2027?"
- "What is ZDHC and how much does it cost in PKR?"
- "My buyer is asking for OEKO-TEX. Where do I start in Karachi?"
- "What chemicals are banned in EU textile exports?"

---

## Architecture
User Query
↓
Node 1 — Query Classifier     → identifies query category (9 types)
↓
Node 2 — Product Detector     → identifies textile product type
↓
Node 3 — RAG Retriever        → searches ChromaDB regulation database
↓
Node 4 — Gap Analyser         → detects missing certifications
↓
Node 5 — Action Plan          → generates phase by phase plan
↓
Node 6 — Compliance Scorer    → scores readiness 0 to 100
↓
Node 7 — Consultation Trigger → shows booking link if score < 60
↓
Node 8 — Final Answer         → Claude synthesizes complete response
↓
Streamlit UI — displays answer + compliance dashboard

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Model | Claude Haiku (Anthropic) |
| Agent Framework | LangGraph |
| Vector Database | ChromaDB |
| Embedding Model | all-MiniLM-L6-v2 (local, free) |
| Web UI | Streamlit |
| Language | Python 3.10 |
| Security | bleach input sanitization |

---

## Knowledge Base

DPPBot has 6 EU regulation files built into its ChromaDB:

| File | Contents |
|------|----------|
| espr_regulation.txt | ESPR Article 7, DPP timelines, penalties |
| reach_requirements.txt | SVHC substances, testing requirements, banned chemicals |
| zdhc_guide.txt | ZDHC levels, costs in PKR, approved labs in Pakistan |
| certifications_guide.txt | OEKO-TEX, GOTS, GRS, Bluesign, ISO 14001, SA8000 |
| product_specific.txt | Denim, knitwear, home textiles, garments requirements |
| pakistan_exporter_guide.txt | GSP Plus, local labs, PKR costs, common mistakes |

---

## Compliance Scoring

| Score | Status |
|-------|--------|
| 0 — 30 | 🔴 NOT READY |
| 31 — 60 | 🟡 PARTIAL |
| 61 — 80 | 🔵 MOSTLY READY |
| 81 — 100 | 🟢 COMPLIANT |

---

## Project Structure
DPPBot/
├── app.py                          ← Streamlit web app
├── DPPBot_Notebook1_Setup.ipynb    ← Project setup and data generation
├── DPPBot_Notebook2_ChromaDB.ipynb ← Vector database and RAG pipeline
├── DPPBot_Notebook3_Agent.ipynb    ← LangGraph agent
├── README.md                       ← This file
└── dppbot/
├── .env                        ← API key (not in GitHub)
├── data/
│   ├── exporters.json          ← 30 synthetic exporter profiles
│   ├── queries.json            ← 25 test query scenarios
│   ├── db_info.json            ← ChromaDB metadata
│   ├── agent_config.json       ← Agent configuration
│   └── regulations/            ← 6 EU regulation text files
└── chromadb_store/             ← Vector database (auto generated)

---

## Setup Instructions

### Step 1 — Clone and navigate
```bash
git clone https://github.com/yourusername/DPPBot.git
cd DPPBot
```

### Step 2 — Install dependencies
```bash
pip install anthropic chromadb python-dotenv pandas sentence-transformers streamlit langchain langchain-anthropic langgraph bleach reportlab pdfplumber
```

### Step 3 — Add your API key
Create `dppbot/.env` and add:
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
Get your key at console.anthropic.com

### Step 4 — Run the notebooks in order
DPPBot_Notebook1_Setup.ipynb   → Run all cells
DPPBot_Notebook2_ChromaDB.ipynb → Run all cells
DPPBot_Notebook3_Agent.ipynb   → Run all cells

### Step 5 — Launch the app
```bash
streamlit run app.py
```
Opens at http://localhost:8501

---

## Security Features

- API key stored in .env file — never in code
- All user input sanitized with bleach library
- Input length limited to 500 characters
- Category whitelist validation — only known categories accepted
- .gitignore protects .env from GitHub upload

---

## Cost

| Item | Cost |
|------|------|
| Anthropic API | ~$0.50 to build and test entire project |
| Embedding model | Free — runs locally |
| ChromaDB | Free — runs locally |
| Streamlit | Free |
| Total | Under $1 |

---

## What I Learned Building This

- How to design a multi-node LangGraph agent pipeline
- How RAG works in practice — chunking, embedding, retrieval
- How to use ChromaDB as a persistent vector store
- How to connect regulation knowledge to AI responses
- Real EU DPP compliance requirements for textile exporters
- How to debug Windows path issues and Python environment conflicts

---

## Portfolio

This is Project 2 in my AI Engineering Portfolio.

- Project 1 — TextileBot
- Project 2 — DPPBot (this project)
- More coming soon

**Junaid Iqbal — AI Engineer**
Website: iamjunaidiqbal.com

---

## License

MIT License — free to use and modify with attribution.
Save that as README.md in your DPPBot folder. Then when you upload to GitHub it will display beautifully on your repository page.