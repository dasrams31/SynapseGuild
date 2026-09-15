# 🏰 SYNAPSEGUILD — 16-Bit Autonomous AI RPG Guildhall ⚔️

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0--Release-amber?style=for-the-badge&logo=shield" />
  <img src="https://img.shields.io/badge/Language-Python%20%7C%20Node.js-38bdf8?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Engine-Phaser.js%203%20%7C%20FastAPI-emerald?style=for-the-badge&logo=phaser" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" />
</p>

<p align="center">
  <b>SynapseGuild</b> adalah ekosistem <i>Autonomous Multi-Agent Dialectical RPG Arena</i> di mana 3 agen kecerdasan buatan (<b>The Sage</b>, <b>The Forge Master</b>, dan <b>The Grand Inquisitor</b>) hidup di dalam sebuah kastil kantor abad pertengahan retro 16-bit. Mereka berkumpul di meja rapat, berdebat menentukan strategi teknis, merakit kode program secara realtime di bengkel, dan bertarung melawan monster <b>"The Bug Beast"</b> di Altar Pengujian sebelum artefak kodingan diserahkan ke Guild Master.
</p>

---

## 🌟 Fitur Utama (Guildhall Features)

```
       🔮 WAR ROOM             ☕ BREAK ROOM          📚 KNOWLEDGE VAULT
   ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
   │ [The Sage]       │ ──> │ [Watercooler ☕] │ ──> │ [Naskah Kuno 📜] │
   │ Blueprint & BDD  │     │ Refill MP 100%   │     │ Template Quests  │
   └──────────────────┘     └──────────────────┘     └──────────────────┘
            │                                                 ▲
            ▼                                                 │
   ┌──────────────────┐                               ┌──────────────────┐
   │ [Forge Master]   │ ────────────────────────────> │ [Sentinel Audit] │
   │ Typewriter Code  │                               │ Boss Battle (Bug)│
   └──────────────────┘                               └──────────────────┘
       ⚒️ THE FORGE                                     ⚖️ TESTING ALTAR
```

- 🎮 **16-Bit Medieval Cyber-Office (Phaser.js 3):** 5 Ruangan interaktif kastil abad pertengahan (*War Room, Break Room/Pantry Lounge, Knowledge Vault, The Forge, Server Lab & QA Altar*).
- 🕹️ **Dual Controls (D-Pad Joystick & Point-and-Click):** Kontrol karakter menggunakan joystick virtual di layar atau klik langsung di lantai.
- 👾 **Live Boss Battle ("The Bug Beast"):** Monster glitch ber-HP bar yang diserang dan dikurangi darahnya saat unit test lolos.
- ☕ **Clickable Facilities:**
  - ☕ **Watercooler/Kopi:** Memulihkan MP party 100%.
  - 📚 **Knowledge Vault:** Auto-load template prompt coding instan ke Quest Board.
  - ⚒️ **Anvil:** Mengasah palu tempa & dorongan koding.
- 💻 **Live Code Forge Inspector:** Tab penampil kode sumber realtime saat *Forge Master* merakit file kodingan.
- 👑 **Guild Master Direct Interventions:** Berikan arahan darurat di tengah perdebatan War Room.
- 🐍/⚡ **Polyglot Forge:** Mendukung pembuatan kode **Python (`pytest`)** dan **JavaScript (`node:test`)**.
- 📦 **The Royal Courier:** Otomatis melakukan commit Git lokal untuk setiap quest yang lolos 100%.
- 🏆 **Guild Hall of Fame & Leveling:** EXP dan Level party yang bertambah setiap kemenangan misi.
- 🎵 **16-Bit Chiptune Web Audio BGM & Favicon:** Musik retro dinamis (Lounge vs Boss Battle) + Favicon pedang kastil.
- ⏳ **Zero-Clutter 15-Minute Auto-Wipe:** Berkas sementara otomatis dihapus dalam 15 menit atau seketika saat diunduh.
- 📱 **Dedicated Telegram Remote Bot (`@synapseguild_bot`):** Kirim perintah `/quest` dan terima file `.zip` langsung di Telegram.

---

## 👥 Para Pahlawan Party AI (The Guild Members)

| Karakter | Peran | Deskripsi Kemampuan |
|---|---|---|
| 🧙‍♂️ **The Sage (Architect)** | *Strategist & Planner* | Membedah quest menjadi spesifikasi teknis modular & kriteria penerimaan pengujian (BDD). |
| ⚒️ **The Forge Master (Craftsman)** | *Engineer & Builder* | Menempa kode bersih, modular, dan membuat unit test mandiri tanpa placeholder/stubs. |
| ⚖️ **The Grand Inquisitor (Sentinel)** | *Zero-Trust Auditor* | Mengeksekusi pengujian di sandbox terisolasi, menyerang monster Bug Beast, dan memberi audit kelulusan 100%. |

---

## 🚀 Panduan Instalasi Cepat (1-Click Installer)

### 1. Clone Repository
```bash
git clone https://gitlab.com/RamsNotes31/synapseguild-rpg-agent.git
cd synapseguild-rpg-agent
```

### 2. Jalankan Wizard Installer Interaktif
```bash
chmod +x install.sh
./install.sh
```
*Installer akan otomatis membuat virtual environment, menginstal dependensi, dan menanyakan API Key AI pilihan Anda (OpenAI, OpenRouter, Groq, DeepSeek, Ollama, dll).*

---

## ⚙️ Konfigurasi Manual (`.env`)

Jika ingin mengatur variabel lingkungan secara manual:

```bash
cp .env.example .env
nano .env
```

Isi parameter berikut:
```ini
# 🧠 Konfigurasi AI Gateway (Mendukung semua format OpenAI-compatible)
SYNAPSE_AI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx
SYNAPSE_AI_BASE_URL=https://openrouter.ai/api/v1
SYNAPSE_AI_MODEL=deepseek/deepseek-chat

# 📱 Dedicated Telegram Remote Bot (Opsional)
SYNAPSE_TELEGRAM_BOT_TOKEN=8818582573:AAGKKZUww...
SYNAPSE_ADMIN_CHAT_ID=606533609

# 🌐 Server Settings
SYNAPSE_PORT=8100
SYNAPSE_HOST=0.0.0.0
SYNAPSE_CLEANUP_TTL_SECONDS=900
```

---

## 🎮 Menjalankan Guildhall

Jalankan server menggunakan script peluncur:
```bash
./start.sh
```

Buka peramban browser Anda di:
👉 **`http://localhost:8100`**

---

## 📱 Menggunakan Telegram Remote Controller

Jika Anda mengaktifkan bot Telegram:
1. Buka bot Telegram Anda (contoh: `@synapseguild_bot`).
2. Kirim perintah:
   ```text
   /quest Buatkan modul kalkulator kalori pendakian dan unit test pytest-nya
   ```
3. Saksikan pergerakan karakter dan diskusinya di layar web secara realtime.
4. Begitu pengujian lolos 100%, berkas **`.zip` artefak kodingan akan otomatis dikirimkan langsung ke ruang obrolan Telegram Anda!**

---

## 🏛️ Arsitektur Direktori Proyek

```text
SynapseGuild/
├── 📜 install.sh           # 1-Click Interactive Setup Wizard
├── 🚀 start.sh             # Application Launcher Script
├── 📄 requirements.txt     # Python Dependencies
├── ⚙️ .env.example         # Environment Configuration Blueprint
├── 📁 docs/
│   └── 📄 PRD.md           # Product Requirements Document
├── 📁 backend/
│   ├── 🐍 app.py           # FastAPI Core, WebSockets & REST Endpoints
│   ├── 🐍 orchestrator.py  # 3-Agent Dialectical Execution Pipeline
│   ├── 🐍 llm.py           # Universal OpenAI-Compatible Multi-Provider Client
│   ├── 🐍 sandbox_runner.py# Isolated Code Sandbox (pytest & node:test)
│   ├── 🐍 git_courier.py   # Royal Courier Git Auto-Commit Service
│   ├── 🐍 telegram_bot.py  # Dedicated Telegram Remote Controller
│   └── 📁 agents/
│       ├── 🧙‍♂️ architect.py      # The Sage Agent Logic
│       ├── ⚒️ craftsman.py      # The Forge Master Agent Logic
│       ├── ⚖️ sentinel.py       # The Grand Inquisitor Auditor Logic
│       └── 💬 dialogue_engine.py# War Room Consensus Discussion Engine
└── 📁 frontend/
    └── 🌐 index.html       # Phaser.js 3 16-Bit Medieval Office GUI + Web Audio BGM
```

---

## 📜 Lisensi & Kontribusi

Dikembangkan dengan penuh dedikasi oleh **Rama Danadipa (@RamsNotes31 / @dasrams)**.  
Dilisensikan di bawah naungan **MIT License**.
Semua petualang kode dipersilakan untuk *fork*, mengajukan *pull request*, dan membangun ruang petualangan AI multi-agen bersama! ⚔️🏰✨
