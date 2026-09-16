import os
import json
import time
import requests
import zipfile
import io
import threading
from typing import Optional

API_BASE_URL = "http://127.0.0.1:8100/api"
ADMIN_CHAT_ID = "606533609"
BOT_TOKEN = "8818582573:AAGKKZUwwgrKk0nR3Z88Z875NRcvzlsuWIQ"

def send_telegram_message(bot_token: str, chat_id: str, text: str, parse_mode: str = "Markdown"):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending TG msg: {e}")

def send_telegram_document(bot_token: str, chat_id: str, file_bytes: bytes, filename: str, caption: str = ""):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    try:
        files = {"document": (filename, file_bytes, "application/zip")}
        data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
        requests.post(url, data=data, files=files, timeout=30)
    except Exception as e:
        print(f"Error sending TG doc: {e}")

def monitor_and_deliver_quest(quest_id: str, bot_token: str, chat_id: str, title: str, language: str = "python"):
    """Background thread to poll quest progress and deliver zip file upon completion."""
    max_wait = 240
    start = time.time()
    
    while time.time() - start < max_wait:
        time.sleep(3)
        try:
            res = requests.get(f"{API_BASE_URL}/quests/{quest_id}", timeout=5)
            if res.status_code == 200:
                data = res.json()
                status = data.get("status")
                
                if status == "completed":
                    result = data.get("result", {})
                    score = result.get("score", 100)
                    files = list(result.get("files", {}).keys())
                    review = result.get("review", "Semua pengujian lolos.")
                    
                    # Fetch ZIP artifact directly
                    zip_res = requests.get(f"{API_BASE_URL}/quests/{quest_id}/download?auto_wipe=false", timeout=15)
                    if zip_res.status_code == 200:
                        caption = (
                            f"🏆 *QUEST SELESAI & THE BUG BEAST K.O!* ⚔️✨\n\n"
                            f"📜 *Quest:* {title}\n"
                            f"🐍 *Language:* `{language.upper()}`\n"
                            f"📊 *Skor Sentinel:* `{score}/100` (Tests Passed)\n"
                            f"📦 *File Terlampir:* {', '.join(f'`{f}`' for f in files)}\n"
                            f"📝 *Review:* _{review}_\n\n"
                            f"⚠️ *Catatan Storage:* Berkas sementara di server otomatis dihapus setelah *15 menit* demi efisiensi storage."
                        )
                        send_telegram_document(bot_token, chat_id, zip_res.content, f"{quest_id}_artifacts.zip", caption)
                    else:
                        send_telegram_message(bot_token, chat_id, f"✅ Quest selesai! Skor: {score}/100. File: {', '.join(files)}")
                    break
                elif status == "failed":
                    send_telegram_message(bot_token, chat_id, f"❌ *Quest Gagal:* Batas iterasi habis atau pengujian belum terpenuhi.")
                    break
        except Exception as e:
            print(f"Error monitoring quest: {e}")

def run_telegram_listener(bot_token: str, admin_chat_id: str):
    offset = None
    print(f"🏛️ SynapseGuild Dedicated Telegram Bot Listener started for Admin ID: {admin_chat_id}")
    
    try:
        commands = [
            {"command": "quest", "description": "Dispatch misi baru ke 3 AI Agent (Hasil ZIP dikirim)"},
            {"command": "quest_js", "description": "Dispatch misi JavaScript/Node.js ke 3 AI Agent"},
            {"command": "status", "description": "Cek kesehatan party, storage TTL & WebSocket link"},
            {"command": "help", "description": "Panduan remote control SynapseGuild"}
        ]
        requests.post(f"https://api.telegram.org/bot{bot_token}/setMyCommands", json={"commands": commands}, timeout=5)
    except Exception:
        pass

    session = requests.Session()

    while True:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            params = {"timeout": 15}
            if offset:
                params["offset"] = offset
                
            resp = session.get(url, params=params, timeout=25)
            data = resp.json()
            
            if not data.get("ok"):
                time.sleep(2)
                continue
                
            for update in data.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                chat_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "").strip()
                
                # STRICT ACCESS: Only Admin Mas Rama
                if chat_id != str(admin_chat_id):
                    send_telegram_message(bot_token, chat_id, "⛔ *Akses Ditolak:* Bot ini eksklusif sebagai Remote Control SynapseGuild untuk Admin.")
                    continue
                    
                if text.startswith("/start") or text.startswith("/help"):
                    welcome = (
                        "🏛️ *SYNAPSEGUILD AI PARTY REMOTE* ⚔️\n\n"
                        "Selamat datang, Guild Master Mas Rama!\n\n"
                        "Gunakan bot ini untuk memerintah party 3 AI Agent secara remote:\n"
                        "• `/quest <perintah>` ➔ Dispatch misi Python (`pytest`)\n"
                        "• `/quest_js <perintah>` ➔ Dispatch misi JavaScript (`node:test`)\n"
                        "• `/status` ➔ Cek status server, party & Boss Altar\n"
                        "• `/help` ➔ Bantuan navigasi\n\n"
                        "💡 *Contoh: `/quest Buatkan modul kalkulator kalori pendakian dan unit test pytest-nya`*"
                    )
                    send_telegram_message(bot_token, chat_id, welcome)
                    
                elif text.startswith("/quest") or text.startswith("/quest_js"):
                    is_js = text.startswith("/quest_js")
                    prefix_len = 9 if is_js else 6
                    prompt = text[prefix_len:].strip()
                    language = "javascript" if is_js else "python"
                    
                    if not prompt:
                        send_telegram_message(bot_token, chat_id, f"⚠️ Masukkan instruksi quest setelah command. Contoh:\n`/{ 'quest_js' if is_js else 'quest' } Buat fungsi kalkulator BMI`")
                        continue
                        
                    title = prompt[:45] + ("..." if len(prompt) > 45 else "")
                    send_telegram_message(
                        bot_token, 
                        chat_id, 
                        f"⚔️ *QUEST [{language.upper()}] DITERIMA & DIDISPATCH!* 📜\n\n"
                        f"🎯 *Tujuan:* *\"{prompt}\"*\n\n"
                        f"Party (*The Sage, Forge Master, Sentinel*) mulai berkumpul di War Room untuk merancang dan merakit kode.\n"
                        f"📁 *Setelah 100% lolos uji, file .ZIP akan otomatis dikirimkan ke chat ini.* (TTL: 15 menit)\n"
                        f"🌐 Pantau visual arena di: `https://rpg.dasrams.biz.id`"
                    )
                    
                    try:
                        res = requests.post(f"{API_BASE_URL}/quest/dispatch", json={
                            "title": title,
                            "prompt": prompt,
                            "language": language,
                            "preset": "classic",
                            "difficulty": "normal",
                            "author": "Guild Master Rama (Telegram Remote)"
                        }, timeout=10)
                        
                        if res.status_code == 200:
                            q_data = res.json()
                            quest_id = q_data.get("quest_id")
                            
                            threading.Thread(
                                target=monitor_and_deliver_quest,
                                args=(quest_id, bot_token, chat_id, title, language),
                                daemon=True
                            ).start()
                        else:
                            send_telegram_message(bot_token, chat_id, f"❌ Gagal mendaftarkan quest ke Gateway: {res.text}")
                    except Exception as err:
                        send_telegram_message(bot_token, chat_id, f"❌ Error koneksi ke Gateway: {err}")
                        
                elif text.startswith("/status") or text.startswith("/health"):
                    try:
                        res = requests.get(f"{API_BASE_URL}/health", timeout=5)
                        if res.status_code == 200:
                            status_msg = (
                                "🟢 *SYNAPSEGUILD ENGINE ONLINE* 🏛️✨\n\n"
                                "• *Web Arena:* `https://rpg.dasrams.biz.id`\n"
                                "• *WebSocket:* `WSS Live Link Active`\n"
                                "• *Party:* The Sage, Forge Master, Sentinel\n"
                                "• *Boss Altar:* The Bug Beast (LV.99)\n"
                                "• *Storage Policy:* `15 Menit Auto-Wipe TTL`\n"
                                "• *Git Courier:* Auto-Commit Enabled"
                            )
                            send_telegram_message(bot_token, chat_id, status_msg)
                        else:
                            send_telegram_message(bot_token, chat_id, "🟡 Gateway merespons dengan status non-200.")
                    except Exception as err:
                        send_telegram_message(bot_token, chat_id, f"🔴 Gateway offline: {err}")
                        
        except Exception as e:
            session = requests.Session()
            time.sleep(2)

if __name__ == "__main__":
    run_telegram_listener(BOT_TOKEN, ADMIN_CHAT_ID)
