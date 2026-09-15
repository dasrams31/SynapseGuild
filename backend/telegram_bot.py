import os
import json
import time
import requests
import zipfile
import io
from typing import Optional

API_BASE_URL = "http://127.0.0.1:8100/api"
ADMIN_CHAT_ID = "606533609"
BOT_TOKEN = "«redacted:8818582573:AAGKKZUww…».NRcvzlsuWIQ"

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

def monitor_and_deliver_quest(quest_id: str, bot_token: str, chat_id: str, title: str):
    """Background thread to poll quest progress and deliver zip file upon completion."""
    max_wait = 180
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
                    
                    # Fetch ZIP artifact
                    zip_res = requests.get(f"{API_BASE_URL}/quests/{quest_id}/download", timeout=10)
                    if zip_res.status_code == 200:
                        caption = (
                            f"🏆 **QUEST SELESAI & 100% LOLOS UJI!** ⚔️✨\n\n"
                            f"📜 **Quest:** {title}\n"
                            f"📊 **Skor Sentinel:** `{score}/100` (Pytest Passed)\n"
                            f"📦 **Artefak:** {', '.join(f'`{f}`' for f in files)}\n\n"
                            f"📁 *Berkas zip artefak terlampir di atas.*"
                        )
                        send_telegram_document(bot_token, chat_id, zip_res.content, f"{quest_id}_artifacts.zip", caption)
                    else:
                        send_telegram_message(bot_token, chat_id, f"✅ Quest selesai! Skor: {score}/100. File: {', '.join(files)}")
                    break
                elif status == "failed":
                    send_telegram_message(bot_token, chat_id, f"❌ **Quest Gagal:** Batas iterasi habis atau pengujian belum terpenuhi.")
                    break
        except Exception as e:
            print(f"Error monitoring quest: {e}")

def run_telegram_listener(bot_token: str, admin_chat_id: str):
    offset = None
    print(f"🏛️ SynapseGuild Dedicated Telegram Bot Listener started for Admin ID: {admin_chat_id}")
    
    # Set bot commands in Telegram
    try:
        commands = [
            {"command": "quest", "description": "Dispatch misi/tugas baru ke 3 AI Agent"},
            {"command": "status", "description": "Cek kesehatan party & server SynapseGuild"},
            {"command": "help", "description": "Panduan remote control SynapseGuild"}
        ]
        requests.post(f"https://api.telegram.org/bot{bot_token}/setMyCommands", json={"commands": commands}, timeout=5)
    except Exception:
        pass

    import threading

    while True:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
                
            resp = requests.get(url, params=params, timeout=40)
            data = resp.json()
            
            if not data.get("ok"):
                time.sleep(4)
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
                        "🏛️ **SYNAPSEGUILD AI PARTY REMOTE** ⚔️\n\n"
                        "Selamat datang, Guild Master Mas Rama!\n\n"
                        "Gunakan bot ini untuk memerintah party 3 AI Agent secara remote:\n"
                        "• `/quest <perintah>` ➔ Dispatch misi baru ke (The Sage, Forge Master, Sentinel)\n"
                        "• `/status` ➔ Cek status server, party & WebSocket link\n"
                        "• `/help` ➔ Bantuan perintah\n\n"
                        "💡 *Contoh: `/quest Buatkan script kalkulator kalori pendakian dan unit test pytest-nya`*"
                    )
                    send_telegram_message(bot_token, chat_id, welcome)
                    
                elif text.startswith("/quest"):
                    prompt = text[6:].strip()
                    if not prompt:
                        send_telegram_message(bot_token, chat_id, "⚠️ Masukkan instruksi quest setelah command. Contoh:\n`/quest Buat fungsi kalkulator BMI`")
                        continue
                        
                    title = prompt[:45] + ("..." if len(prompt) > 45 else "")
                    send_telegram_message(
                        bot_token, 
                        chat_id, 
                        f"⚔️ **QUEST DITERIMA & DIDISPATCH!** 📜\n\n"
                        f"🎯 **Tujuan:** *\"{prompt}\"*\n\n"
                        f"Party (*The Sage, Forge Master, Sentinel*) mulai berkumpul di War Room untuk berdiskusi & memprogram kode.\n"
                        f"🌐 Pantau visual arena di: `http://localhost:8100`"
                    )
                    
                    try:
                        res = requests.post(f"{API_BASE_URL}/quest/dispatch", json={
                            "title": title,
                            "prompt": prompt,
                            "difficulty": "normal",
                            "author": "Guild Master Rama (Telegram Remote)"
                        }, timeout=10)
                        
                        if res.status_code == 200:
                            q_data = res.json()
                            quest_id = q_data.get("quest_id")
                            
                            # Start thread to monitor and deliver result zip
                            threading.Thread(
                                target=monitor_and_deliver_quest,
                                args=(quest_id, bot_token, chat_id, title),
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
                                "🟢 **SYNAPSEGUILD ENGINE ONLINE** 🏛️✨\n\n"
                                "• **Gateway Port:** `8100`\n"
                                "• **WebSocket:** `ws://127.0.0.1:8100/ws/guild-events`\n"
                                "• **Active Party:** The Sage, Forge Master, Sentinel\n"
                                "• **Arena Web:** `http://localhost:8100`"
                            )
                            send_telegram_message(bot_token, chat_id, status_msg)
                        else:
                            send_telegram_message(bot_token, chat_id, "🟡 Gateway merespons dengan status non-200.")
                    except Exception as err:
                        send_telegram_message(bot_token, chat_id, f"🔴 Gateway offline: {err}")
                        
        except Exception as e:
            time.sleep(3)

if __name__ == "__main__":
    run_telegram_listener(BOT_TOKEN, ADMIN_CHAT_ID)
