<div align="center">

  <a href="https://gitlab.com/RamsNotes31/synapseguild-rpg-agent">
    <img src="assets/logo.svg" alt="SynapseGuild Logo" width="220" height="220" />
  </a>

  <h1>⚔️ SYNAPSEGUILD 🏰</h1>
  <h3>Autonomous AI Multi-Agent RPG Guildhall Arena</h3>

  <p>
    <em>A 16-bit retro medieval cyber-office where autonomous AI agents deliberate in the War Room, forge production-ready code in the Workshop, and cooperatively battle "The Bug Beast" in the Sandbox Judgment Altar.</em>
  </p>

  <p>
    <a href="https://gitlab.com/RamsNotes31/synapseguild-rpg-agent"><img src="https://img.shields.io/badge/GitLab-Repository-fc6d26?style=for-the-badge&logo=gitlab&logoColor=white" alt="GitLab" /></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
    <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/Node.js-18+-339933?style=for-the-badge&logo=node.js&logoColor=white" alt="Node.js" /></a>
    <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
    <a href="https://phaser.io/"><img src="https://img.shields.io/badge/Phaser.js-3.80+-8B5CF6?style=for-the-badge&logo=javascript&logoColor=white" alt="Phaser.js 3" /></a>
    <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/TailwindCSS-v3-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-amber?style=for-the-badge" alt="License" /></a>
  </p>

</div>

---

## 📖 Table of Contents
- [✨ Overview](#-overview)
- [🏰 The Expanded 7-Room Castle World](#-the-expanded-7-room-castle-world)
- [🔐 Mandatory Guild Passport & User Persistence](#-mandatory-guild-passport--user-persistence)
- [👥 The 3-Agent Party Roster](#-the-3-agent-party-roster)
- [🎮 Interactive Facilities & Boss Raid](#-interactive-facilities--boss-raid)
- [🚀 Quick Start (1-Click Installer)](#-quick-start-1-click-installer)
- [⚙️ Manual Configuration (`.env`)](#-manual-configuration-env)
- [📱 Dedicated Telegram Bot Remote Control](#-dedicated-telegram-bot-remote-control)
- [📁 Repository Structure](#-repository-structure)
- [📜 License & Credits](#-license--credits)

---

## ✨ Overview

**SynapseGuild** bridges **Autonomous Multi-Agent LLM Orchestration** with **2D Retro Game Visualizations**. Instead of static text streams or black-box terminal outputs, your AI agents inhabit a living, interactive 16-bit medieval office castle:

1. **Dialectical Consensus Engine:** Agents gather around the **War Room Table** to debate architectural trade-offs, algorithms, and test boundaries before typing a single line of code.
2. **Polyglot Code Forge:** *The Forge Master* assembles modular Python (`pytest`) or JavaScript (`node:test`) code with live typewriter inspection.
3. **Cooperative Boss Raid Battle:** Agents storm the **Boss Altar** and unleash combo attacks (*Arcane Beam, Forge Smash, Holy Slash*) on **"The Bug Beast"**, draining its HP bar as test suites pass with 100% scores.
4. **Royal Courier & Auto-Wipe TTL:** Approved code artifacts are logged to Git, downloadable as `.zip`, delivered via Telegram, and automatically purged after 15 minutes for zero storage clutter.

---

## 🏰 The Expanded 7-Room Castle World

```
 🔮 1. WAR ROOM       ☕ 2. BREAK ROOM      📚 3. ARCHIVE VAULT   💎 4. CRYSTAL GARDEN
 ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
 │ [Planning Table]│  │ [Watercooler ☕] │  │ [Bookshelves 📜] │  │ [Mana Shard 💎]  │
 │ Blueprint & BDD │  │ Refill MP 100%   │  │ Load Templates   │  │ Absorb +25 EXP   │
 └─────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
          │                                                                ▲
          ▼                                                                │
 ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────────────────┐
 │ [Anvil & Forge] │  │ [Hero Beds 🛌]   │  │ 🔥 7. BOSS RAID ARENA                   │
 │ Dev Workshop    │  │ Rest Quarters    │  │ [The Bug Beast] vs 3-Agent Raid Attack  │
 └─────────────────┘  └──────────────────┘  └─────────────────────────────────────────┘
 ⚒️ 5. THE FORGE      🛌 6. HERO DORMITORY
```

---

## 🔐 Mandatory Guild Passport & User Persistence

SynapseGuild features a **built-in SQLite User Authentication & Quest History System (`guild_users.db`)**:

- 🛡️ **Mandatory Login / Registration:** Users must register or log in with their Adventurer Passport to access the Guildhall.
- 🧙‍♂️ **Custom RPG Roles & Avatars:** Choose your Class Role (*Wizard, Knight, Paladin, Blacksmith*) and custom avatar icons upon registration.
- 📜 **Personalized Quest History:** Every quest dispatched is recorded in the user's personal vault with pass/fail status, test scores, and direct file access.
- 👑 **Default Master Account:**
  - **Username:** `dasrams`
  - **Password:** `dasrams123`
  - **Title:** *Grand Guild Master (Level 99 • Crown Avatar)*

---

## 👥 The 3-Agent Party Roster

| Agent Avatar | Character Title | RPG Class | Core Responsibility |
|:---:|:---|:---:|:---|
| 🧙‍♂️ | **The Sage** | *High Wizard / Architect* | Decomposes raw prompts into modular file plans, interface definitions, and strict BDD acceptance criteria. |
| ⚒️ | **The Forge Master** | *Blacksmith / Craftsman* | Implements clean, dependency-free, production-grade Python or JavaScript code with matching unit tests. |
| ⚖️ | **The Grand Inquisitor** | *Paladin / Sentinel* | Executes zero-trust automated test runners (`pytest` / `node:test`) in isolated sandboxes and deals the final blow to bugs. |

---

## 🎮 Interactive Facilities & Boss Raid

- 🕹️ **On-Screen D-Pad & Click-To-Move:** Navigate any character across all 7 rooms using the 16-bit virtual joystick or mouse clicks.
- ☕ **Watercooler & Coffee Dispenser:** Click the pantry dispenser to trigger a coffee gulp SFX and replenish party MP back to 100%.
- 💎 **Arcane Mana Shard (Crystal Garden):** Click the glowing crystal shard to absorb pure mana and gain **+25 EXP** instantly.
- 📚 **Knowledge Vault & Bookshelves:** Click the library bookcases to automatically inject battle-tested coding templates (Calories, Naismith Rule, Temperature, etc.) directly into the Quest Board.
- ⚒️ **Forge Terminal & Anvil:** Click the workshop anvil to sharpen blacksmith tools and boost coding morale.
- 🛌 **Hero Dormitory:** Rest your characters in the cozy quarters between intense coding quests.
- 👑 **Guild Master Live Interventions:** Dispatch immediate course-corrections (*"Use simpler modular approach"*, *"Add extreme boundary tests"*) during live War Room debates.
- 🎵 **Adaptive 16-Bit Chiptune BGM:** Built-in Web Audio chiptune synthesizer that dynamically transitions between peaceful lounge melodies and high-octane Boss Battle tracks.
- 🏆 **Guild Hall of Fame & Leveling:** Complete quests to earn **+100 EXP**, trigger level-ups (`LV.1 -> LV.99`), and record permanent victory tablets.

---

## 🚀 Quick Start (1-Click Installer)

### 1. Clone the Repository
```bash
git clone https://gitlab.com/RamsNotes31/synapseguild-rpg-agent.git
cd synapseguild-rpg-agent
```

### 2. Run the Interactive Wizard Installer
```bash
chmod +x install.sh
./install.sh
```

The installer will automatically:
- Check Python 3.10+ and Node.js environments.
- Create an isolated `venv` and install backend dependencies.
- Prompt for your **AI Provider / LLM API Key** (OpenAI, OpenRouter, Groq, DeepSeek, Ollama, etc.).
- Initialize the SQLite database and default credentials.
- Generate the executable launcher script `./start.sh`.

### 3. Launch the Guildhall
```bash
./start.sh
```

Open your browser and enter the arena:
👉 **`http://localhost:8100`** *(or `https://rpg.dasrams.biz.id`)*

---

## ⚙️ Manual Configuration (`.env`)

You can manually edit `.env` to connect any OpenAI-compatible LLM endpoint:

```ini
# 🧠 Universal AI Gateway Configuration
SYNAPSE_AI_BASE_URL=https://openrouter.ai/api/v1
SYNAPSE_AI_MODEL=deepseek/deepseek-chat
SYNAPSE_AI_API_KEY=sk-or-v1-your-api-key-here

# 📱 Dedicated Telegram Remote Controller (Optional)
SYNAPSE_TELEGRAM_BOT_TOKEN=8818582573:AAGKKZUwwgrKk0nR3Z88Z875NRcvzlsuWIQ
SYNAPSE_ADMIN_CHAT_ID=606533609

# 🌐 Server & Storage Settings
SYNAPSE_PORT=8100
SYNAPSE_HOST=0.0.0.0
SYNAPSE_CLEANUP_TTL_SECONDS=900
```

---

## 📱 Dedicated Telegram Bot Remote Control

Control your AI party on the go without opening a browser:

1. Create a bot via `@BotFather` and retrieve your token.
2. Put the token and your Telegram User ID in `.env`.
3. Send commands directly to your bot:
   ```text
   /quest Build a mountain hike Naismith time estimation calculator with pytest suite
   ```
4. Watch the party gather and fight on the web interface in real time.
5. Once tests achieve 100% pass, **the bot immediately delivers the zipped code artifact directly to your Telegram chat!**

---

## 📁 Repository Structure

```text
synapseguild-rpg-agent/
├── 📜 install.sh              # 1-Click Interactive Setup Wizard
├── 🚀 start.sh                # Automated Service Launcher
├── 📄 requirements.txt        # Python Backend Dependencies
├── ⚙️ .env.example            # Environment Blueprint
├── 📜 QUEST_LOGS.md           # The Royal Courier Automated Git Victory Tablet
├── 📁 assets/
│   └── 🎨 logo.svg            # 16-Bit Pixel RPG Castle Logo
├── 📁 docs/
│   └── 📄 PRD.md              # Full Product Requirements Document
├── 📁 backend/
│   ├── 🐍 app.py              # FastAPI Engine, WebSocket Hub & REST API
│   ├── 🐍 auth.py             # SQLite Authentication & Quest History Engine
│   ├── 🗄️ guild_users.db      # SQLite User & Quest Database
│   ├── 🐍 orchestrator.py     # 3-Agent Dialectical Consensus Pipeline
│   ├── 🐍 llm.py              # Universal Multi-Provider LLM Client
│   ├── 🐍 sandbox_runner.py   # Isolated Code Sandbox (pytest & node:test)
│   ├── 🐍 git_courier.py      # Royal Courier Git Auto-Commit Service
│   ├── 🐍 telegram_bot.py     # Dedicated Telegram Remote Bot Listener
│   └── 📁 agents/
│       ├── 🧙‍♂️ architect.py         # The Sage Agent Logic
│       ├── ⚒️ craftsman.py         # The Forge Master Agent Logic
│       ├── ⚖️ sentinel.py          # The Grand Inquisitor Auditor Logic
│       └── 💬 dialogue_engine.py   # War Room Consensus Discussion Engine
└── 📁 frontend/
    └── 🌐 index.html          # Phaser 3 16-Bit Medieval Office Canvas & Retro Audio
```

---

## 📜 License & Credits

- **Author & Lead Architect:** Rama Danadipa ([@RamsNotes31](https://gitlab.com/RamsNotes31) / [@dasrams](https://github.com/dasrams))
- **Live Deployment:** [rpg.dasrams.biz.id](https://rpg.dasrams.biz.id)
- **License:** [MIT License](LICENSE)

*Built for AI engineers, open-source explorers, and retro gaming enthusiasts. May your tests always pass and your party never run out of Mana!* ⚔️🏰👾☕🚀
