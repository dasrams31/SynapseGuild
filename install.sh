#!/usr/bin/env bash
# ==============================================================================
# ⚔️ SYNAPSEGUILD — 1-CLICK INTERACTIVE INSTALLER & WIZARD
# Autonomous Multi-Agent AI RPG Guildhall System
# Developed by Rama Danadipa (@RamsNotes31 / @dasrams)
# ==============================================================================

set -e

CYAN='\033[0;36m'
AMBER='\033[0;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${AMBER}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║             ⚔️  SYNAPSEGUILD AI RPG GUILDHALL INSTALLER  ⚔️           ║"
echo "║          Autonomous Multi-Agent Dialectical Consensus Platform        ║"
echo "║               Developed by Rama Danadipa (@RamsNotes31)               ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKDIR"

echo -e "${CYAN}[1/4] 🔍 Checking system dependencies...${NC}"
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+ first.${NC}"; exit 1; }

echo -e "${GREEN}✓ Python 3 detected: $(python3 --version)${NC}"

# Check Node.js
if command -v node >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Node.js detected: $(node -v) (Polyglot JS Forge active)${NC}"
else
    echo -e "${AMBER}⚠️ Node.js not detected (Python pytest runner remains active).${NC}"
fi

echo ""
echo -e "${CYAN}[2/4] 📦 Setting up Virtual Environment & Python Modules...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment 'venv' created.${NC}"
fi

source venv/bin/activate
pip install --upgrade pip >/dev/null 2>&1 || true
pip install -r requirements.txt --prefer-offline --no-audit >/dev/null 2>&1 || pip install fastapi uvicorn websockets pydantic pytest requests pyyaml httpx

echo -e "${GREEN}✓ All backend dependencies (FastAPI, WebSockets, Pytest, Uvicorn) are ready!${NC}"

echo ""
echo -e "${CYAN}[3/4] 🧠 AI Gateway & LLM API Configuration...${NC}"
echo -e "SynapseGuild supports any OpenAI-compatible API (OpenAI, OpenRouter, Groq, DeepSeek, Ollama, etc)."
echo ""

if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || touch .env
fi

read -p "👉 Enter LLM Base URL [Default: https://openrouter.ai/api/v1]: " INPUT_BASE_URL
BASE_URL=${INPUT_BASE_URL:-"https://openrouter.ai/api/v1"}

read -p "👉 Enter Model Name [Default: deepseek/deepseek-chat]: " INPUT_MODEL
MODEL_NAME=${INPUT_MODEL:-"deepseek/deepseek-chat"}

read -p "👉 Enter your AI API Key: " INPUT_API_KEY
API_KEY=${INPUT_API_KEY:-""}

read -p "👉 Enable Dedicated Telegram Remote Bot? (y/N): " ENABLE_TG
if [[ "$ENABLE_TG" =~ ^[Yy]$ ]]; then
    read -p "   Enter Telegram Bot Token (@BotFather): " TG_TOKEN
    read -p "   Enter Admin Telegram Chat ID: " TG_ADMIN_ID
else
    TG_TOKEN=""
    TG_ADMIN_ID=""
fi

# Write to .env
cat <<EOF > .env
# SynapseGuild Environment Config
SYNAPSE_AI_BASE_URL=${BASE_URL}
SYNAPSE_AI_MODEL=${MODEL_NAME}
SYNAPSE_AI_API_KEY=${API_KEY}
SYNAPSE_TELEGRAM_BOT_TOKEN=${TG_TOKEN}
SYNAPSE_ADMIN_CHAT_ID=${TG_ADMIN_ID}
SYNAPSE_PORT=8100
SYNAPSE_HOST=0.0.0.0
SYNAPSE_CLEANUP_TTL_SECONDS=900
EOF

echo -e "${GREEN}✓ .env configuration saved successfully!${NC}"

echo ""
echo -e "${CYAN}[4/4] 🚀 Initializing Database & Launcher Script...${NC}"

# Initialize SQLite database
python3 backend/auth.py >/dev/null 2>&1 || true

cat << 'EOF' > start.sh
#!/usr/bin/env bash
WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKDIR"

source venv/bin/activate
export $(grep -v '^#' .env | xargs -d '\n') 2>/dev/null || true

echo "🏰 Launching SynapseGuild AI Engine on port ${SYNAPSE_PORT:-8100}..."

# Launch Telegram bot in background if token is provided
if [ -n "$SYNAPSE_TELEGRAM_BOT_TOKEN" ]; then
    echo "📱 Launching Dedicated Telegram Remote Bot..."
    python3 backend/telegram_bot.py > /dev/null 2>&1 &
fi

cd backend
python3 -m uvicorn app:app --host ${SYNAPSE_HOST:-0.0.0.0} --port ${SYNAPSE_PORT:-8100}
EOF
chmod +x start.sh

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 INSTALLATION COMPLETE & SYNAPSEGUILD IS READY! 🏰✨${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "👉 Default Admin Account for Login:"
echo -e "   Username: ${AMBER}dasrams${NC}"
echo -e "   Password: ${AMBER}dasrams123${NC}"
echo ""
echo -e "👉 Start the server now:"
echo -e "   ${AMBER}./start.sh${NC}"
echo ""
echo -e "🌐 Open the Visual RPG Arena in your browser:"
echo -e "   ${CYAN}http://localhost:8100${NC}"
echo ""
echo -e "⚔️ Enjoy your adventure with your autonomous AI Party! 🎮"
