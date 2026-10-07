# JARVIS — Desktop AI Assistant

> **A voice-first desktop AI assistant that combines conversational AI, persistent memory, multimodal perception, and controlled computer automation through a futuristic desktop interface.**

JARVIS is a Python-based desktop AI assistant designed to interact naturally with a computer through **voice and keyboard input**.

It combines AI reasoning with a modular action system, local memory, computer interaction, and a custom HUD to turn natural-language requests into useful desktop actions.

The project is actively evolving toward a **hybrid AI architecture**, combining cloud intelligence with local LLMs through Ollama.

---

## ✨ Features

### 🧠 AI Assistant

- Google Gemini-powered conversational intelligence
- Natural-language task understanding
- Context-aware conversations
- Persistent local memory
- Intelligent task and action routing
- Keyboard and voice interaction

### 🎙️ Voice Interaction

- Wake-word activation
- Speech-to-text input
- Text-to-speech responses
- Natural voice conversations
- Voice activity feedback

### 🖥️ Desktop Automation

JARVIS can interact with the desktop through controlled application actions, including:

- Launching applications
- Browser interaction
- File operations
- System utilities
- Media control
- Reminders
- Information retrieval
- Other modular desktop actions

### 👁️ Multimodal Interaction

JARVIS is designed to work beyond text by supporting visual interaction capabilities such as:

- Screen analysis
- Webcam analysis
- Visual understanding
- AI-assisted interpretation of on-screen content

### 🎨 JARVIS HUD

A custom PyQt-based interface provides a futuristic control layer for the assistant.

- Holographic-style HUD
- Animated interface elements
- Assistant state indicators
- Voice activity visualization
- Dark futuristic interface
- Real-time interaction feedback

---

## 🏗️ Architecture

JARVIS follows a modular architecture where user input is interpreted, routed, and then handled by the appropriate AI or action component.

```text
                    ┌──────────────────────┐
                    │       USER           │
                    │  Voice / Keyboard    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    INPUT LAYER       │
                    │ STT / Text / Wake    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   AI / ROUTING CORE  │
                    │ Intent + Reasoning   │
                    └──────────┬───────────┘
                               │
                  ┌────────────┼────────────┐
                  │            │            │
                  ▼            ▼            ▼
             ┌─────────┐ ┌──────────┐ ┌──────────┐
             │ Gemini  │ │  Ollama  │ │  Memory  │
             │ Online  │ │  Local   │ │  System  │
             └────┬────┘ └─────┬────┘ └────┬─────┘
                  │             │            │
                  └─────────────┼────────────┘
                                ▼
                    ┌──────────────────────┐
                    │     ACTION LAYER     │
                    │ Desktop / Web / Apps │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     JARVIS HUD       │
                    │  Response / Status   │
                    └──────────────────────┘
```

---

## 🔀 Hybrid AI

One of the major development directions of JARVIS is a hybrid AI architecture.

```text
                 User Request
                      │
                      ▼
                Request Router
                      │
             ┌────────┴────────┐
             │                 │
       Internet Available?     │
             │                 │
          ┌──┴──┐              │
         YES    NO              │
          │      │              │
          ▼      ▼              │
       Gemini  Ollama           │
       Online   Local           │
          │      │              │
          └──┬───┘              │
             ▼                  │
        Action / Response ◄─────┘
```

The goal is to allow JARVIS to use cloud-based AI when connectivity is available while providing a local execution path through **Ollama and local LLMs**.

> **Offline AI support is currently under active development.**

---

## 🧩 Core Components

| Component | Purpose |
|---|---|
| **AI Core** | Reasoning and conversational intelligence |
| **Request Router** | Determines how a request should be handled |
| **Action Layer** | Performs controlled desktop and web operations |
| **Memory System** | Stores and retrieves persistent context |
| **Voice Layer** | Wake word, STT and TTS interaction |
| **Vision Layer** | Screen and camera understanding |
| **JARVIS HUD** | Visual interface and system feedback |
| **Local AI** | Ollama-based local model execution |

---

## 🛠️ Technology Stack

### Core

- Python
- PyQt
- Modular Python architecture

### AI

- Google Gemini
- Ollama
- Local Large Language Models

### Voice

- Speech-to-Text
- Text-to-Speech
- Wake-word detection
- Voice activity processing

### Perception

- Screen analysis
- Webcam analysis
- Multimodal AI interaction

### Automation

- Desktop application control
- Browser interaction
- File operations
- System utilities

### Memory

- Local persistent memory
- Conversation context
- User-specific preferences

---

## 📁 Project Structure

```text
JARVIS2/
│
├── actions/              # Desktop and task execution modules
├── core/                 # Core AI and assistant logic
├── memory/               # Persistent memory and context
├── config/               # Local configuration
├── ui/                   # JARVIS interface and HUD
├── models/               # Model-related components
│
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── setup.py              # Project configuration
└── .gitignore            # Repository exclusions
```

> **API credentials and other sensitive configuration files are intentionally excluded from version control.**

---

## 🚀 Getting Started

### Requirements

- Python 3.10+
- Windows 10/11
- Microphone for voice interaction
- Internet connection for cloud AI features
- Ollama for local AI features

### 1. Clone the repository

```bash
git clone https://github.com/melvingeo-04/Desktop-AI-Assistant.git
cd Desktop-AI-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure local credentials

Create your local configuration file according to the project's configuration requirements.

**Never commit API keys, access tokens, or credentials to GitHub.**

### 5. Run JARVIS

```bash
python main.py
```

---

## 🔐 Security

JARVIS is designed around **controlled computer interaction** rather than unrestricted model execution.

Key principles include:

- API credentials remain outside version control
- AI responses are handled through application-controlled logic
- System operations are exposed through defined action modules
- Sensitive configuration is excluded from Git
- Arbitrary model-generated commands should not be executed blindly

Security and reliability remain ongoing development priorities as the assistant gains more autonomous capabilities.

---

## 🧪 Development Status

JARVIS is an actively evolving project.

### Current development

- [x] Gemini-based AI interaction
- [x] Voice interaction
- [x] Keyboard interaction
- [x] Persistent memory
- [x] Desktop action system
- [x] Custom JARVIS HUD
- [x] Screen/webcam analysis
- [ ] Ollama integration
- [ ] Automatic online/offline routing
- [ ] Expanded local-model capabilities
- [ ] Further reliability and safety improvements

---

## 🗺️ Roadmap

### Phase 1 — Core Assistant
- Conversational AI
- Voice interaction
- Desktop automation
- Persistent memory

### Phase 2 — Hybrid Intelligence
- Ollama integration
- Local LLM support
- Automatic network-aware routing
- Online/offline mode switching

### Phase 3 — Advanced Agent
- Improved planning
- More modular tools
- Better multimodal reasoning
- Stronger execution safeguards
- More autonomous task workflows

---

## 🎯 Vision

The goal of JARVIS is not simply to create another chatbot.

The goal is to build a **personal desktop intelligence layer** capable of connecting:

```text
       Natural Language
              │
       ┌──────▼──────┐
       │     AI      │
       └──────┬──────┘
              │
      ┌───────┼────────┐
      │       │        │
    Memory  Vision  Reasoning
      │       │        │
      └───────┼────────┘
              │
        Computer Control
              │
              ▼
            JARVIS
```

A system that can **understand what you ask, reason about what needs to happen, interact with the computer, remember useful context, and increasingly operate locally when privacy or connectivity demands it.**

---

## 👨‍💻 Author

**Melvin George**

B.Tech Computer Science & Engineering

GitHub: [@melvingeo-04](https://github.com/melvingeo-04)

---

## 📌 Project

**Repository:**  
https://github.com/melvingeo-04/Desktop-AI-Assistant

JARVIS is developed as an ongoing personal AI engineering project exploring **desktop agents, multimodal AI, local LLMs, intelligent automation, and human-computer interaction**.
