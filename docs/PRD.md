# Product Requirements Document (PRD)
# Project: SynapseGuild — Autonomous Multi-Agent AI RPG Guildhall

---

## 1. Executive Summary & Vision

**SynapseGuild** is an autonomous multi-agent orchestration and development environment presented through an interactive, retro 2.5D / Pixel-Art RPG Guildhall interface. 

Instead of traditional, dry AI agent command-line outputs, SynapseGuild models an autonomous "party" of three specialized AI agents (The Sage/Architect, The Craftsman/Forge Master, and The Sentinel/Grand Inquisitor) collaborating, debating, generating solutions, executing tests in sandboxed environments, and reaching consensus to fulfill complex programming, research, and data processing quests.

The system features **dual-ingress control**:
1. **Interactive Web Quest Board** with real-time visual simulation (Phaser.js/Next.js) showing live sprite pathfinding, speech bubbles, battle/crafting telemetry, and artifact loot drops.
2. **Dedicated Telegram Bot Remote** allowing the admin to dispatch quests on the go, receive realtime status broadcasts, and download generated artifacts.

---

## 2. Core Personas & Multi-Agent Architecture (The Party)

SynapseGuild enforces a formal dialectical consensus workflow (Thesis ➔ Antithesis ➔ Synthesis) among three distinct roles:

```text
               ┌──────────────────────────────────────────────────────────┐
               │              1. THE ARCHITECT / SAGE                     │
               │  Class: Planner & Strategist                             │
               │  Duties: Goal decomposition, system specs, BDD criteria  │
               └────────────────────────────┬─────────────────────────────┘
                                            │ (Technical Blueprint)
                                            ▼
               ┌──────────────────────────────────────────────────────────┐
               │             2. THE CRAFTSMAN / FORGE MASTER              │
               │  Class: Builder & Implementer                            │
               │  Duties: Code generation, tool execution, refactoring    │
               └────────────────────────────┬─────────────────────────────┘
                                            │ (Candidate Artifacts)
                                            ▼
               ┌──────────────────────────────────────────────────────────┐
               │            3. THE SENTINEL / GRAND INQUISITOR            │
               │  Class: Zero-Trust Auditor & Tester                      │
               │  Duties: Code review, vulnerability audit, sandbox test  │
               └────────────────────────────┬─────────────────────────────┘
                                            │
               [Rejected / Score < 85%] ────┴────► [Approved / 100% Passed]
             (Re-enters Forge for Revision)            (Quest Complete! Loot Dropped)
```

### Role Specifications:
1. **The Architect (The Sage):**
   - **Archetype:** Tactical planner and arbitrator.
   - **Responsibilities:** Takes high-level prompts from the Quest Board or Telegram Bot, breaks them down into task DAGs, sets explicit acceptance criteria (Gherkin/BDD tests), and intervenes during agent deadlocks.
   - **Zone:** *The War Room* (Round Table).

2. **The Craftsman (The Forge Master):**
   - **Archetype:** High-velocity builder and engineer.
   - **Responsibilities:** Implements clean, modular code, leverages sandboxed tools, runs initial file writes, and iterates on fixes based on Sentinel feedback.
   - **Zone:** *The Forge & Workshop* (Anvil & Terminal Workstation).

3. **The Sentinel (The Grand Inquisitor):**
   - **Archetype:** Strict adversarial auditor and QA engineer.
   - **Responsibilities:** Executes code in an ephemeral Docker/subprocess sandbox, runs automated unit tests (`pytest`, `vitest`), verifies edge cases, and provides structured severity scoring.
   - **Zone:** *The Chamber of Judgment* (Magic Inspection Altar).

---

## 3. RPG Gamification & Realtime Telemetry Mapping

All visual game elements directly reflect real computational and operational metrics:

| RPG Game Mechanic | Real System Metric | In-Game Visual Behavior |
|---|---|---|
| 🔴 **HP (Health Points)** | **Error Tolerance & Retry Budget** | Deducts on syntax errors, failed test runs, or runtime exceptions. Reaching 0 triggers party wipe / strategy revision by Architect. |
| 🔵 **MP (Mana Points)** | **Context Window & Token Budget** | Decreases as prompt tokens and reasoning steps increase. Regenerates during context compaction or idle Tavern states. |
| 🛡️ **Defense / Armor** | **Test Coverage % & Type-Safety** | Computed from `pytest-cov` / TypeScript strictness. Mitigates HP damage from edge-case failures. |
| ⭐ **EXP & Leveling** | **Completed Quest Count** | Agents gain experience and level up, unlocking persisted skill snippets in vector memory. |
| 🎒 **Inventory / Artifacts** | **Available Toolsets & Plugins** | Displayed as collectible RPG gear (e.g., *Blade of Terminal*, *Scroll of Vector Search*, *Shield of Linting*). |
| ⚡ **Buffs & Debuffs** | **System State Events** | • *Flow State:* API latency < 1.0s (+Speed)<br>• *Context Saturation:* Context > 80% (-Mana)<br>• *Rate Limit Stun:* HTTP 429 backoff animation |

---

## 4. Visual & Interface Design Specifications

### 4.1. The 2.5D Guildhall Map Zones
The canvas renders a cohesive pixel-art or isometric guildhall divided into interactive rooms:
1. **The War Room:** Round table where agents gather for initial quest briefing and planning debates.
2. **The Forge:** Workshop with an anvil, workbench, and mini live terminal screen displaying streaming code.
3. **The Chamber of Judgment:** Mystic circle where Sentinel performs verification with visual particle effects (green lightning for pass, red storm for test failure).
4. **The Great Archive:** Bookshelves accessed during RAG/documentation vector lookups.
5. **The Tavern:** Rest zone where idle agents relax with ambient banter when no quest is active.

### 4.2. UI Components & Layout
- **Top Bar:** Guild Master stats, active LLM model selector (Gemini-3.7-Flash / Custom 9Router / Claude), global token burn rate.
- **Center Canvas:** Phaser.js 3 game view supporting viewport zooming, sprite pathfinding, dynamic speech bubbles, and character click interactions.
- **Left Drawer:** Quest Board (Active quest details, sub-task checklist, difficulty selector).
- **Right Drawer:** Live Terminal & Debate Transcript (Raw stdout, diffs, and structured debate logs).
- **Bottom Bar:** Time-Travel Replay Bar (Scrubber to review previous turns) + Human Intervention ("Summon Party" button).

---

## 5. Dual-Ingress Workflow Specification

```text
                  ┌──────────────────────┐      ┌─────────────────────────┐
                  │ Web Quest Board UI   │      │ Dedicated Telegram Bot  │
                  └──────────┬───────────┘      └────────────┬────────────┘
                             │                               │
                             └───────────────┬───────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │    SynapseGuild API Gateway   │
                             │   (FastAPI + WebSocket Hub)   │
                             └───────────────┬───────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
          [3-Agent Cyclic Engine]                       [Realtime Event Stream]
        (LangGraph / State Machine)                     (Phaser.js Game Canvas)
```

### Ingress 1: Web Quest Board
- Users fill out Quest Title, Target Description, Acceptance Criteria, and attach files (GPX, specs, docs).
- Option to select Party Mode (*Full Autonomous* vs *Human Approval Gate*).
- Realtime visual feedback as the party moves across the canvas.

### Ingress 2: Dedicated Telegram Bot Remote
- Isolated Telegram Bot dedicated exclusively to the Admin.
- Commands:
  - `/quest <description>`: Dispatches a new quest to the party.
  - `/status`: Returns party HP/MP, current phase, and active room.
  - `/pause` / `/resume`: Controls autonomous execution.
  - `/loot`: Retrieves and downloads the latest completed quest artifacts (.py, .json, .zip).
- Receives milestone push notifications (Quest Started ➔ Code Tested ➔ Passed/Failed).

---

## 6. Technical Stack & Infrastructure

```text
SynapseGuild/
├── backend/
│   ├── app.py                 # FastAPI Application & WebSocket Server
│   ├── orchestrator.py        # LangGraph Multi-Agent Cyclic Graph
│   ├── agents/
│   │   ├── base.py            # Base Agent ABC & Event Emitter
│   │   ├── architect.py       # The Sage (Planning & Specs)
│   │   ├── craftsman.py       # The Forge Master (Code & Execution)
│   │   └── sentinel.py        # The Grand Inquisitor (Testing & Security Audit)
│   ├── sandbox/               # Isolated Subprocess / Container Execution Runner
│   ├── telegram_bot.py        # Dedicated Admin Telegram Controller
│   └── database/              # SQLite / PostgreSQL for Quest State & Artifacts
├── frontend/                  # Next.js 14 (App Router) + TailwindCSS
│   ├── components/
│   │   ├── GuildCanvas.tsx    # Phaser.js 3 Canvas Wrapper & Event Handlers
│   │   ├── QuestBoard.tsx     # Quest Dispatcher & Task Checklist
│   │   ├── PartyStatus.tsx    # RPG HP/MP/EXP HUD
│   │   └── TerminalLogs.tsx   # Live Streaming Log Terminal
│   └── public/assets/         # Pixel-Art Spritesheets, Tilesets, Audio SFX
└── docs/                      # PRD, Architecture Specs, and Setup Guides
```

- **Frontend:** Next.js 14, React 18, Phaser.js 3, Lucide Icons, TailwindCSS.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, LangGraph / LangChain, WebSockets.
- **LLM Gateway:** 9Router (Port 20128) / OpenAI API / Anthropic API compatibility.
- **Isolation Sandbox:** Docker ephemeral runner / restricted virtualenv subprocesses.
- **Persistence:** SQLite for session state, JSON for quest artifacts.

---

## 7. Execution Roadmap

- **Phase 1: Multi-Agent Consensus Engine & Sandbox**
  - Implement LangGraph state machine with Architect ➔ Craftsman ➔ Sentinel loop.
  - Build sandbox runner for automated `pytest` / execution verification.
- **Phase 2: FastAPI Event Stream & Dedicated Telegram Bot**
  - Implement WebSocket event broadcaster emitting sprite coordinates, emotes, and dialogues.
  - Build standalone Telegram bot for remote quest dispatching and artifact delivery.
- **Phase 3: Phaser.js 2.5D Guildhall Frontend**
  - Assemble guildhall map (War Room, Forge, Judgment Chamber, Archive, Tavern).
  - Implement sprite animations, pathfinding, speech bubbles, and RPG HUD.
- **Phase 4: Advanced Features & Polish**
  - Implement Time-Travel replay scrubber, artifact loot drops, and sound effects.
