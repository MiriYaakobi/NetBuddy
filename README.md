# 🎓 Study Agent Pro

> An AI-powered study assistant tailored for computer networking courses, featuring semantic RAG (Retrieval-Augmented Generation), automated subnet calculations, security guardrails, and a sleek cyber-lilac Streamlit UI.

---

## 🏗️ Architecture Overview

The system follows a modular ReAct agent architecture, combining local vector search with Groq's LLM API:

    [User (Streamlit UI)] -> [Security Guardrails] -> [Agent Loop (ReAct)] -> [Groq LLM]
                                                               |
                                                    [Tools: ChromaDB / Calc]
                                                               |
                                                    [Logging & Token Control]

---

## 📊 Performance & Metrics

| Metric | Result |
| :--- | :--- |
| **Eval Pass Rate** | High accuracy on core networking tasks |
| **Average Steps per Task** | 2 - 3 steps |
| **Token Optimization** | Optimized short-term memory (last 4 messages) |
| **Response Time** | ~3.2 seconds average |

---

## 🛠️ Tech Stack & Tools

* Core Language: Python 3.13
* Package Management: uv
* LLM API: Groq (Qwen / Llama models)
* Vector Database: ChromaDB (for local course notes RAG)
* UI Framework: Streamlit (Cyberpunk-Lilac custom CSS)

---

## ⚙️ Installation & Setup

Follow these steps to set up and run the project locally:

1. Clone the repository:
   git clone [https://github.com/MiriYaakobi/study-agent.git](https://github.com/MiriYaakobi/study-agent.git)
   cd study-agent

2. Install dependencies using uv:
   uv sync

3. Configure environment variables:
   Create a .env file in the root directory and add your Groq API key:
   GROQ_API_KEY=your_actual_api_key_here

---

## 🚀 Usage

### 1. Run the Terminal Agent Tests
To evaluate the agent's logic, tool-calling, and security guardrails:
   uv run eval.py

### 2. Launch the Streamlit Web Interface
To open the interactive web application in your browser:
   uv run streamlit run app.py

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.