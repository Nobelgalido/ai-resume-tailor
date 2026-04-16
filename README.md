# 🎯 AI Resume Tailor

> An end-to-end AI-powered resume optimization tool that tailors your resume to any job description and exports an ATS-safe PDF — built with Claude AI, Streamlit, and fpdf2.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Anthropic](https://img.shields.io/badge/Claude_AI-191919?style=for-the-badge&logo=anthropic&logoColor=white)
![fpdf2](https://img.shields.io/badge/fpdf2-007ACC?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

---

## 📸 Screenshots

> _Add screenshots of your app here after deployment_
> 
> Suggested screenshots:
> - Upload screen
> - ATS Audit Results with score metric
> - Generated PDF output

---

## 🧠 How It Works — Three-Agent Architecture

```
📄 Your Resume (PDF)
        │
        ▼
┌───────────────────┐
│  PDF Text         │  pdfplumber extracts raw text
│  Extractor        │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Agent 1          │  Claude Haiku
│  The Extractor    │  Parses resume → structured JSON
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Agent 2          │  Claude Sonnet
│  The Tailor       │  Rewrites resume for keyword alignment
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Agent 3          │  Claude Haiku
│  The Auditor      │  Scores ATS match (0-100)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  PDF Generator    │  fpdf2 generates ATS-safe PDF
│                   │  with clickable links
└───────────────────┘
```

- **Agent 1 — Extractor (Haiku):** Converts raw resume text into structured JSON
- **Agent 2 — Tailor (Sonnet):** Rewrites resume content to mirror job description keywords
- **Agent 3 — Auditor (Haiku):** Scores the ATS match and suggests improvements

> Using different models intentionally — Sonnet for complex rewriting, Haiku for structured tasks. This keeps API costs low while maximizing quality.

---

## 🚀 Features

- 📄 Upload any text-based resume PDF
- 🤖 Three-agent Claude AI pipeline
- 🎯 ATS keyword alignment and optimization
- 📊 ATS compatibility score with matched/missing keywords
- 📥 Download ATS-safe PDF with clickable LinkedIn & GitHub links
- 🔒 API key protected via `.env` file

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Streamlit` | Reactive web UI |
| `Anthropic Python SDK` | Claude AI API calls |
| `pdfplumber` | PDF text extraction |
| `fpdf2` | ATS-safe PDF generation |
| `python-dotenv` | API key management |

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com)

### 1. Clone the Repository

```bash
git clone https://github.com/Nobelgalido/ai-resume-tailor.git
cd ai-resume-tailor
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows (Git Bash)
source venv/Scripts/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example env file
cp .env.example .env
```

Open `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 5. Run the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📁 Project Structure

```
ai-resume-tailor/
├── app.py              # Streamlit UI + pipeline orchestration
├── agents.py           # Three Claude AI agents
├── pdf_generator.py    # ATS-safe PDF generation
├── requirements.txt    # Project dependencies
├── .env.example        # API key template (safe to commit)
├── .env                # Your actual API key (gitignored)
├── .gitignore          # Protects secrets and venv
└── README.md
```

---

## 🔒 Security

- API keys are stored in `.env` — never committed to Git
- `.gitignore` blocks `.env`, `venv/`, and generated PDFs
- See `.env.example` for required environment variables

---

## 📖 Lessons Learned

This project was built lesson by lesson covering:

| Lesson | Topic |
|---|---|
| 0 | Version control & API key safety |
| 1 | Python virtual environments & Streamlit UI |
| 2 | PDF text extraction & file I/O |
| 3 | Three-agent Claude AI architecture |
| 4 | Session state & pipeline data flow |
| 5 | ATS-safe PDF generation with fpdf2 |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 👤 Author

**Alfred Nobel F. Galido**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/alfrednobelgalido)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Nobelgalido)
