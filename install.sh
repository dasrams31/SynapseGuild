#!/usr/bin/env bash
# ==============================================================================
# ⚔️ SYNAPSEGUILD — 1-CLICK INTERACTIVE INSTALLER & WIZARD
# Autonomous Multi-Agent RPG Guildhall System
# Developed by Rama Danadipa (@RamsNotes31)
# ==============================================================================

set -e

CYAN='\033[0;36m'
AMBER='\033[0;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

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

echo -e "${CYAN}[1/4] 🔍 Memeriksa dependensi sistem...${NC}"
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3 tidak ditemukan. Harap instal Python 3.10+ terlebih dahulu.${NC}"; exit 1; }

echo -e "${GREEN}✓ Python 3 terdeteksi: $(python3 --version)${NC}"

# Check Node.js
if command -v node >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Node.js terdeteksi: $(node -v) (Polyglot JS Forge siap)${NC}"
else
    echo -e "${AMBER}⚠️ Node.js tidak terdeteksi (Polyglot JavaScript test runner dinonaktifkan, Python tetap aktif).${NC}"
fi

echo ""
echo -e "${CYAN}[2/4] 📦 Menyiapkan Virtual Environment & Dependencies...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment 'venv' berhasil dibuat.${NC}"
fi

source venv/bin/activate
pip install --upgrade pip >/dev/null 2>&1 || true
pip install -r requirements.txt --prefer-offline --no-audit >/dev/null 2>&1 || pip install fastapi uvicorn websockets pydantic pytest requests pyyaml httpx jinja2

echo -e "${GREEN}✓ Semua modul backend (FastAPI, WebSockets, Pytest, Uvicorn) siap!${NC}"

echo ""
echo -e "${CYAN}[3/4] 🧠 Konfigurasi Kunci AI Gateway (LLM API Setup)...${NC}"
echo -e "SynapseGuild mendukung semua API yang kompatibel dengan format OpenAI (OpenAI, OpenRouter, Groq, DeepSeek, Ollama, dll)."
echo ""

if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || touch .env
fi

read -p "👉 Masukkan Base URL LLM [Default: https://openrouter.ai/api/v1]: " INPUT_BASE_URL
BASE_URL=${INPUT_BASE_URL:-"https://openrouter.ai/api/v1"}

read -p "👉 Masukkan Model Name [Default: deepseek/deepseek-chat]: " INPUT_MODEL
MODEL_NAME=${INPUT_MODEL:-"deepseek/deepseek-chat"}

read -p "👉 Masukkan API Key Anda: " INPUT_API_KEY
API_KEY=${INPUT_API_KEY:-""}

read -p "👉 Ingin mengaktifkan Telegram Remote Bot? (y/N): " ENABLE_TG
if [[ "$ENABLE_TG" =~ ^[Yy]$ ]]; then
    read -p "   Masukkan Telegram Bot Token (@BotFather): " TG_TOKEN
    read -p "   Masukkan Admin Telegram Chat ID: " TG_ADMIN_ID
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

echo -e "${GREEN}✓ Konfigurasi .env berhasil disimpan!${NC}"

echo ""
echo -e "${CYAN}[4/4] 🚀 Menyiapkan Script Peluncur (Launcher)...${NC}"
cat << 'EOF' > start.sh
#!/usr/bin/env bash
WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKDIR"

source venv/bin/activate
export $(grep -v '^#' .env | xargs -d '\n') 2>/dev/null || true

echo "🏰 Menjalankan SynapseGuild AI Engine di port ${SYNAPSE_PORT:-8100}..."

# Jalankan Telegram Bot di background jika token diisi
if [ -n "$SYNAPSE_TELEGRAM_BOT_TOKEN" ]; then
    echo "📱 Menghubungkan Dedicated Telegram Remote Bot..."
    python3 backend/telegram_bot.py > /dev/null 2>&1 &
fi

cd backend
python3 -m uvicorn app:app --host ${SYNAPSE_HOST:-0.0.0.0} --port ${SYNAPSE_PORT:-8100}
EOF
chmod +x start.sh

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 INSTALASI SELESAI & SYNAPSEGUILD SIAP DIGUNAKAN! 🏰✨${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "👉 Jalankan aplikasi sekarang dengan perintah:"
echo -e "   ${AMBER}./start.sh${NC}"
echo ""
echo -e "🌐 Buka antarmuka Visual RPG Web di browser:"
echo -e "   ${CYAN}http://localhost:8100${NC}"
echo ""
echo -e "⚔️ Selamat bertualang bersama Party AI Anda di SynapseGuild! 🎮"
