<div align="center">

```text
  ███████╗██╗   ██╗███╗   ██╗ █████╗ ██████╗ ███████╗███████╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔════╝
  ███████╗ ╚████╔╝ ██╔██╗ ██║███████║██████╔╝███████╗█████╗  
  ╚════██║  ╚██╔╝  ██║╚██╗██║██╔══██║██╔═══╝ ╚════██║██╔══╝  
  ███████║   ██║   ██║ ╚████║██║  ██║██║     ███████║███████╗
  ╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚══════╝
      ───  A U T O N O M O U S   R P G   G U I L D H A L L  ───
```

# ⚔️ SYNAPSE GUILD : AGENTIC RPG GUILDHALL ⚔️
### ✦ Autonomous Multi-Agent AI Collective with Web Simulation Canvas ✦

[![Guild Status](https://img.shields.io/badge/Guild%20Status-Active%20Sovereign-32CD32?style=for-the-badge&logo=superflux&logoColor=white)](#-guild-architecture)
[![Agent Swarm](https://img.shields.io/badge/Agent%20Swarm-Multi--Role%20Specialists-8A2BE2?style=for-the-badge&logo=openai&logoColor=white)](#-guild-roster--specialist-classes)
[![Live Interface](https://img.shields.io/badge/Port-8100%20(Local%20%26%20Tunnel)-FF4500?style=for-the-badge&logo=fastapi&logoColor=white)](#-summoning--installation)

<p align="center">
  <i>"Where autonomous AI agents take on RPG guild roles—taking quests, writing code in isolated sandboxes, reviewing peer outputs, and evolving abilities in real time."</i>
</p>

---

</div>

## 🏰 ✦ Guild Architecture & State Machine ✦

```text
                     ┌──────────────────────────────────┐
                     │    👑 GUILDMASTER (Admin / Core)  │
                     └─────────────────┬────────────────┘
                                       │ Dispatch Quest
                                       ▼
                     ┌──────────────────────────────────┐
                     │   📜 GUILD QUEST BOARD (Queue)    │
                     └─────────────────┬────────────────┘
                                       │ Assign Class
               ┌───────────────────────┼───────────────────────┐
               ▼                       ▼                       ▼
      ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
      │  🗡️ DEV KNIGHT   │     │  🔮 ARCH-MAGE   │     │  🛡️ SENTINEL    │
      │  (Code Artisan) │     │  (AI Synthesis) │     │  (QA & Defense) │
      └────────┬────────┘     └────────┬────────┘     └────────┬────────┘
               │                       │                       │
               └───────────────────────┼───────────────────────┘
                                       │ Execute in Isolation
                                       ▼
                     ┌──────────────────────────────────┐
                     │    🧪 DYNAMIC QUEST SANDBOX      │
                     │  (Isolated Subprocess & Pytest)  │
                     └─────────────────┬────────────────┘
                                       │ Validate Solution
                                       ▼
                     ┌──────────────────────────────────┐
                     │  🏆 REWARD ENGINE & LEVEL UP!    │
                     │  (EXP, Gold, Badges & History)   │
                     └──────────────────────────────────┘
```

---

## 👥 ✦ Guild Roster & Specialist Classes ✦

| Class Crest | Specialist Name | Domain & Ability | Weapon of Choice |
| :---: | :--- | :--- | :--- |
| 🗡️ | **Dev-Knight** | Algorithm craft, syntax mastery, automated refactoring | Python 3.14, Node.js, Pytest |
| 🔮 | **Inference-Mage** | Multi-model prompt weaving, cognitive planning & reasoning | Gemini 2.5 Flash, Claude 3.7 |
| 🛡️ | **Aegis-Sentinel** | Zero-trust validation, test assertion verification, sandboxing | Subprocess Jails, SARIF Audits |
| 🏹 | **Scout-Ranger** | Web asset reconnaissance, DOM parsing & API harvesting | Async HTTPX, BeautifulSoup |
| 💰 | **Treasury-Alchemist** | Quest reward computation, EXP progression, SQLite ledger | SQLite, JSONL Transactions |

---

## 🎮 ✦ Key Features & Enchantments ✦

- **Interactive Visual Canvas**: Retro-futuristic dark mode RPG interface with pixel art aesthetics and real-time audio cues.
- **Automated Sandbox Jails**: Quests spawn dynamic sub-environments where AI code is verified against strict test assertions before earning EXP.
- **Quest Dispatch & Claim System**: Real-time WebSocket streaming of agent thoughts, terminal logs, and execution traces.
- **Persistent Adventurer Records**: SQLite-backed character profiles, inventory items, quest history, and level scaling.

---

## ⚡ ✦ Summoning & Installation ✦

### 1. Clone the Grimoire
```bash
git clone https://github.com/dasrams31/SynapseGuild.git
cd SynapseGuild
```

### 2. Prepare the Alchemical Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Ignite the Guildhall Server
```bash
python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8100 --reload
```

---

<div align="center">

<i>Crafted with passion by **Rama Danadipa (@dasrams)** • Master of the Synapse Guild</i>

</div>
