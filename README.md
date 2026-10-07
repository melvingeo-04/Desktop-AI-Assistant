# 🌟 JARVIS Desktop AI Assistant

![JARVIS](https://img.shields.io/badge/JARVIS-AI-ff8c00?style=for-the-badge&logo=jarvis)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![PyQt](https://img.shields.io/badge/PyQt-6.5+-green?style=for-the-badge&logo=pyqt)

> **Desktop AI Assistant** is an advanced, open-source desktop application that brings the power of AI directly to your computer. Built with Python, PyQt6, and cutting-edge AI models, JARVIS acts as your intelligent personal assistant, productivity booster, and creative partner.

## ✨ Key Features

### 🧠 Advanced AI Capabilities
- **LLM Integration**: Powered by multiple AI models including Google Gemini, OpenAI, and more (customizable via API keys)
- **Voice Interaction**: Natural language understanding with Text-to-Speech (TTS) and Speech-to-Text (STT) support
- **Smart Context**: Maintains conversation history and user preferences for personalized interactions
- **Creative Tools**: Image generation, code assistance, and content creation

### 🎨 Immersive UI Experience
- **Holographic HUD**: 3D holographic interface with stunning animations and visualizations
- **Customizable Themes**: Full color customization with live previews and automatic regeneration
- **Dynamic Visuals**: Real-time waveform analysis, particle effects, and video playback
- **Modern Design**: Sleek, futuristic interface with dark mode and smooth transitions

### 🚀 Powerful Productivity Features
- **Smart Task Management**: Create, track, and manage tasks with AI-powered scheduling
- **File Organization**: Automatic file organization and cleanup suggestions
- **System Automation**: Control system settings and run custom scripts
- **Multi-Plugin Support**: Extend functionality with plugins for file management, system utilities, and more

### 🌐 Seamless Connectivity
- **Web Automation**: Browser control and task automation through Puppeteer
- **Communication**: Send messages and notifications through connected platforms
- **Information Retrieval**: Real-time access to weather, news, and general knowledge
- **Data Sync**: Cloud synchronization for seamless cross-device experience

## 🚀 Getting Started

### Prerequisites
- **Python**: 3.8 or higher
- **pip**: Python package installer
- **Node.js**: For web automation features

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/JARVIS-Desktop-AI.git
    cd JARVIS-Desktop-AI
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Node.js dependencies**
    ```bash
    cd automation/web_automation
    npm install
    cd ..
    ```

4.  **Configure API Keys**
    Create a `config/api_keys.json` file with your API credentials:
    ```json
    {
      "gemini": "YOUR_GEMINI_API_KEY",
      "openai": "YOUR_OPENAI_API_KEY",
      "whatsapp": "YOUR_WHATSAPP_API_KEY"
    }
    ```

### Running the Application

Start JARVIS with a simple command:

```bash
python main.py
```

## 🎨 Customization

### Color Themes

JARVIS supports full color customization. You can change the primary accent color and the entire theme will regenerate automatically.

**Change accent color:**
```python
# In main.py or configuration
app_instance.set_ui_accent("#ff8c00")  # Hex color code
```

**Built-in palettes:**
- `#ff8c00` - Default (Orange)
- `#00d4ff` - Cyan
- `#00ff9d` - Green
- `#ff6b6b` - Red
- `#ffd800` - Yellow

### Interface Configuration

Configure layout and visual preferences:
```python
config = {
    "theme": "dark",
    "accent_color": "#ff8c00",
    "layout": "desktop",
    "show_hud": True,
    "voice_enabled": True,
    "plugins": {
        "weather": {
            "city": "New York",
            "units": "metric"
        }
    }
}
```

## 📂 Project Structure

```
JARVIS-Desktop-AI/
├── core/
│   ├── avatar.py             # Holographic avatar implementation
│   ├── dashboard.py          # Main application dashboard
│   ├── brain.py              # AI model integration and logic
│   └── plugins/              # Plugin architecture
├── automation/
│   ├── web_automation/       # Puppeteer browser automation
│   └── system_automation/    # System control scripts
├── memory/                   # Conversation history and preferences
│   ├── history.json          # Conversation logs
│   └── user_prefs.json       # User settings and preferences
├── ui/
│   ├── widgets/              # Reusable UI components
│   ├── styles/               # CSS stylesheets and themes
│   └── assets/               # Images, icons, and media files
├── config/
│   ├── api_keys.json         # API credentials (DO NOT COMMIT)
│   └── settings.json         # Application settings
├── models/                   # AI model configurations
├── scripts/                  # Utility and helper scripts
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── readme.md                 # Project documentation
```

## 🔌 Plugins

Extend JARVIS functionality with built-in and custom plugins.

### Built-in Plugins
- **Weather**: Real-time weather updates for any location
- **System Utilities**: File management, system monitoring, and automation
- **Web Automation**: Browser control and website interactions
- **Notifications**: Desktop notifications and alerts

### Creating Custom Plugins

Create a new plugin in `core/plugins/`:

```python
from core.plugins.plugin import Plugin

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__("my_plugin", "Description")

    def run(self, args):
        # Plugin logic here
        return "Output message"
```

## 🔧 Development

### Coding Standards
- Adhere to PEP 8 guidelines
- Use type hints for function signatures
- Document all functions and classes
- Keep functions focused and modular

### Testing

Run all tests with:
```bash
python -m pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request



## 📚 Documentation

- [Installation Guide](docs/installation.md) - Detailed installation instructions
- [Configuration Guide](docs/configuration.md) - API and UI configuration
- [Plugin System](docs/plugins.md) - How to create and use plugins
- [Developer Guide](docs/development.md) - Architecture and development standards

## 📞 Support

For issues and questions, please:
1.  Check the [Troubleshooting](docs/troubleshooting.md) guide
2.  Search for similar issues in [Issues](https://github.com/yourusername/JARVIS-Desktop-AI/issues)
3.  Open a new issue with detailed information

## 👥 Credits

Built with ❤️ using:
- **PyQt6**: For the stunning desktop interface
- **Google Gemini**: For advanced AI capabilities
- **Puppeteer**: For web automation
- **Custom Avatar System**: For the holographic HUD

##  🙏 Acknowledgments

Special thanks to:
- The open-source community
- All contributors and testers
- Developers of the libraries and frameworks used