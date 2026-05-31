<p align="center">
  <a href="https://github.com/AmiQT/Chin-Hin">
    <img src="https://img.shields.io/github/stars/AmiQT/Chin-Hin?style=social" alt="GitHub Stars"/>
  </a>
  <br/>
  <img src="https://img.shields.io/badge/Flutter-3.10+-02569B?logo=flutter&logoColor=white" alt="Flutter"/>
  <img src="https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Azure_OpenAI-GPT-0078D4?logo=microsoftazure&logoColor=white" alt="Azure OpenAI"/>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Tests-139_passing-success" alt="Tests"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
</p>

<h1 align="center">Chin-Hin — CHEA (Chin Hin Employee Assistant)</h1>

<p align="center">
  <strong>AI-powered employee assistant dengan natural language interface</strong>
  <br/>
  <em>Meet <b>CHEA</b> — your intelligent workplace companion</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#testing">Testing</a> •
  <a href="#api-reference">API</a> •
  <a href="#documentation">Docs</a>
</p>

---

## Features

<table>
<tr>
<td width="50%">

### AI-Powered Chat (CHEA)
- Natural language understanding (BM + English)
- Context-aware multi-turn conversations
- Multimodal input: **text, voice & images**
- Generative UI cards in chat replies

</td>
<td width="50%">

### Employee Services
- Leave management & balance tracking
- Expense claims with receipt OCR
- Meeting room booking (conflict-aware)
- Transport booking & daily menu

</td>
</tr>
<tr>
<td width="50%">

### Human-in-the-Loop (HITL)
- Sensitive actions (leave/room/transport)
  require explicit confirmation
- Confirmation cards before execution
- Safe-by-default agentic flow

</td>
<td width="50%">

### Proactive Nudges
- AI-generated reminders
- Smart leave-balance notifications
- Background scanning scheduler
- Read/unread tracking

</td>
</tr>
</table>

---

## Tech Stack

<table>
<tr><th>Layer</th><th>Technology</th><th>Purpose</th></tr>
<tr><td>Backend</td><td>FastAPI + Python 3.11</td><td>REST API</td></tr>
<tr><td>AI Engine</td><td>Azure OpenAI (function calling)</td><td>Conversational agent + tools</td></tr>
<tr><td>Receipt OCR</td><td>Azure OpenAI Vision</td><td>Expense receipt extraction</td></tr>
<tr><td>Data Store</td><td>In-Memory (singleton)</td><td>Mock persistence — no external DB needed</td></tr>
<tr><td>Auth</td><td>Token store + DEV_MODE bypass</td><td>Simple bearer-token auth</td></tr>
<tr><td>Mobile</td><td>Flutter + Riverpod + shadcn_ui</td><td>Cross-platform app</td></tr>
</table>

---

## Project Structure

```
Chin-Hin/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # REST endpoints (auth, leaves, claims, rooms, chat...)
│   │   ├── agents/           # Azure OpenAI agentic chat + function tools
│   │   ├── services/         # Data store, OCR, nudges
│   │   └── core/             # Middleware, logging, exceptions, validators
│   ├── tests/                # 102 pytest tests
│   └── requirements.txt
│
├── mobile/                     # Flutter Mobile App
│   ├── lib/
│   │   ├── screens/          # UI screens (login, home, chat, leave, claim, room...)
│   │   ├── providers/        # Riverpod state (user, chat, nudge)
│   │   ├── services/         # API client (Dio)
│   │   └── widgets/          # Generative UI cards
│   └── test/                 # 37 Flutter unit tests
│
└── docs/                       # Documentation
```

---

## Quick Start

### Prerequisites

```bash
Python 3.11+
Flutter SDK 3.10+
Azure OpenAI API Key + deployment
```

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate     # Windows
source venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env        # then fill in your Azure OpenAI keys

# Run server (http://localhost:8000, docs at /docs)
uvicorn app.main:app --reload
```

### Mobile Setup

```bash
cd mobile

# Install dependencies
flutter pub get

# Run in debug (auto-targets localhost:8000, or 10.0.2.2 on Android emulator)
flutter run

# Build release pointing at a deployed backend
flutter build apk --dart-define=API_BASE_URL=https://your-backend.com
```

> In debug mode the app auto-connects to your local backend. For release builds,
> pass the backend URL via `--dart-define=API_BASE_URL=...` — no hardcoded URLs.

---

## Testing

```bash
# Backend (102 tests)
cd backend
pytest -v

# Mobile (37 tests)
cd mobile
flutter test
```

| Suite | Tests | Covers |
|-------|:-----:|--------|
| `backend/tests/test_api.py` | 48 | API endpoints, auth, error handling |
| `backend/tests/test_data_store.py` | 45 | Leave/claim/room/booking logic |
| `backend/tests/test_nudge_service.py` | 9 | Proactive nudge generation |
| `mobile/test/` | 37 | Message model, config, date/time logic |
| **Total** | **139** | all passing |

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | Login (returns bearer token) |
| `/api/v1/chat` | POST | AI chat (text + image) |
| `/api/v1/nudges` | GET | Proactive notifications |
| `/api/v1/leaves/balance` | GET | Leave balance |
| `/api/v1/leaves` | POST | Apply leave |
| `/api/v1/claims/categories` | GET | Claim categories |
| `/api/v1/claims` | POST | Submit expense claim |
| `/api/v1/claims/scan-receipt` | POST | OCR receipt scan |
| `/api/v1/rooms` | GET | Available rooms |
| `/api/v1/rooms/bookings` | POST | Book a room |

> Full documentation: [docs/API.md](docs/API.md) • Interactive docs at `/docs` when running.

---

## Environment Variables

Create `backend/.env` (see [`.env.example`](backend/.env.example)):

```env
# App
ENVIRONMENT=development
DEBUG=true
DEV_MODE=true          # true = bypass auth with mock user; false = require real token

# Azure OpenAI (required for AI chat)
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

> **Never commit `.env`** — it's gitignored. Only `.env.example` (placeholders) is tracked.

---

## Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | Complete API documentation |
| [Frontend Docs](docs/frontend_documentation.md) | Mobile app architecture |
| [AWS Deployment](docs/AWS_DEPLOYMENT.md) | EC2 deployment guide |
| [Quick Start EC2](docs/QUICK_START_EC2.md) | Rapid EC2 deployment |
| [Azure Deployment](docs/DEPLOYMENT.md) | Azure Container Apps steps |

---

## Contributing

1. Fork the [repository](https://github.com/AmiQT/Chin-Hin)
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## License

Licensed under the MIT License. _(Add a `LICENSE` file to formalize this before publishing.)_

---

<p align="center">
  <strong>Built for Chin Hin Group</strong>
  <br/>
  <sub>© 2026 <a href="https://github.com/AmiQT/Chin-Hin">Chin-Hin</a> — Chin Hin Employee AI Assistant (CHEA)</sub>
</p>
