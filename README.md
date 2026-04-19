# 📧 Agentic Email Manager

A production-ready, AI-powered email management system built with **LangGraph**, **GPT-4o**, and the **Gmail API** — featuring a premium **Streamlit** dashboard for visual email triage, AI-generated replies, and smart email composition.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Email Triage** | GPT-4o classifies every email as Work / Personal / Newsletter / Spam |
| 📊 **Priority Detection** | Automatically assigns High / Medium / Low priority |
| 😊 **Sentiment Analysis** | Detects email tone — Urgent, Positive, Neutral, Negative, Curious |
| 📝 **Smart Summarization** | Extracts key points and action items from long emails |
| ✍️ **Tone-Aware Drafting** | Generates replies in 5 tones: Professional, Friendly, Concise, Assertive, Casual |
| 🧑‍💻 **Human-in-the-Loop** | Review, edit, and approve every draft before it's sent |
| 📬 **AI Compose** | Write new emails from just a topic and recipient using GPT-4o |
| 🏢 **Sender Avatars** | Company logos auto-fetched for each email in the inbox |
| 📈 **Analytics Panel** | Live donut chart showing email classification breakdown |
| 🎨 **Premium Dark UI** | Glassmorphism cards, gradient hero banner, live clock |

---

## 🏗️ Architecture

This project is built as a **LangGraph stateful agent** — a directed graph where each node is an AI-powered processing step.

```
fetch → classify → [Spam/Newsletter?] → END
                ↘  [Work/Personal]   → summarize → draft → review → send
```

### LangGraph Concepts Used
- **`StateGraph`** — the workflow container
- **`AgentState`** (TypedDict) — shared data schema across all nodes
- **`Annotated` reducer** (`operator.add`) — for message history merging
- **Nodes** — pure Python functions, one per processing step
- **`add_edge`** — deterministic connections between nodes
- **`add_conditional_edges`** — dynamic routing based on AI classification
- **`compile()`** — validates and locks the graph
- **`invoke()` / `stream()`** — two ways to run the pipeline
- **Human-in-the-Loop** — review gate before any email is sent

---

## 📁 Project Structure

```
Email_Agent/
├── app.py                  # Streamlit dashboard (main UI)
├── main.py                 # CLI mode entry point
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
│
├── graph/
│   ├── state.py            # AgentState TypedDict
│   ├── graph_builder.py    # LangGraph workflow definition
│   └── nodes/
│       ├── fetch_node.py   # Fetches email from Gmail API
│       ├── classify_node.py# GPT-4o: type + priority + sentiment
│       ├── summarize_node.py# GPT-4o: bullet-point summary
│       ├── draft_node.py   # GPT-4o: tone-aware reply draft
│       ├── review_node.py  # Human-in-the-loop approval gate
│       └── send_node.py    # Sends reply via Gmail API
│
├── tools/
│   ├── gmail_tools.py      # Gmail API wrapper functions
│   └── compose_tools.py    # AI new email composer
│
└── utils/
    └── gmail_auth.py       # Google OAuth2 authentication
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- An OpenAI API key
- A Google Cloud project with the **Gmail API** enabled

---

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Email_Agent.git
cd Email_Agent
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-proj-your-key-here
```

### 5. Set Up Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Gmail API** from the API Library
4. Go to **Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Select **Desktop App**, download the JSON file
6. Rename it to `credentials.json` and place it in the project root

### 6. Run the App

```bash
# Launch the Streamlit UI (recommended)
streamlit run app.py

# OR: Run in CLI / terminal mode
python main.py
```

On **first run**, a browser window will open asking you to sign in with Google and grant Gmail access. A `token.json` file is created automatically for future runs.

---

## 🖥️ Using the Dashboard

### 📬 Inbox / Reply Tab
1. Click **"🔄 Refresh"** in the sidebar to load unread emails
2. Select an email — you'll see the sender's company logo, subject, and a priority colour stripe
3. Choose a **Reply Tone** from the dropdown (Professional, Friendly, etc.)
4. Click **"▶️ Run AI Agent"** — the pipeline runs and shows:
   - Classification badge + Priority + Sentiment indicator
   - AI-generated summary of the email
   - Fully editable draft reply
5. Edit the draft if needed, then click **"🚀 Send Reply"**

### ✍️ Compose Tab
1. Enter the recipient's email address
2. Describe what you want to say (e.g. "Schedule a meeting for Thursday")
3. Choose a tone
4. Click **"🤖 Generate Draft"** — GPT-4o writes the full Subject + Body
5. Edit as needed and click **"🚀 Send"**

---

## ⚙️ Tech Stack

| Technology | Purpose |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Stateful agent workflow orchestration |
| [LangChain OpenAI](https://python.langchain.com/) | GPT-4o integration |
| [Gmail API](https://developers.google.com/gmail/api) | Reading and sending emails |
| [Google Auth OAuthLib](https://google-auth-oauthlib.readthedocs.io/) | OAuth2 authentication |
| [Streamlit](https://streamlit.io/) | Web dashboard UI |
| [Plotly](https://plotly.com/python/) | Analytics donut chart |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management |

---

## 🔒 Security Notes

- `credentials.json` and `token.json` are listed in `.gitignore` and will **never** be committed
- Your `.env` file (containing your OpenAI API key) is also excluded
- Never share these files publicly

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🙋‍♂️ Author

**Saad Saddique**  
Built with LangGraph · GPT-4o · Gmail API · Streamlit
