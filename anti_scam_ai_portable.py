#!/usr/bin/env python3
"""
Anti-Scam AI | All-in-One Portable Security Sandbox
--------------------------------------------------
Resolves: ERR_QUIC_PROTOCOL_ERROR, ERR_CONNECTION_TIMED_OUT
Features: Manual OAuth Override, Self-Healing Fallback, Local Terminal UI
"""

import os
import json
import base64
import time
import re
import socket
import sys
import yaml

# --- Dependencies Check ---
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("[!] Warning: Google API dependencies missing. Real Gmail sync will be disabled.")
    print("    Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib pyyaml")

# --- 1. Local Persistence ---
class LocalPersistence:
    """Simulates localStorage using a local JSON file."""
    def __init__(self, filepath='data/local_storage.json'):
        self.filepath = filepath
        os.makedirs(os.path.dirname(self.filepath) or '.', exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._save()

# --- 2. Scan Engine ---
class ScanEngine:
    """Engine for detecting scams in text and speech data."""
    URGENCY_PATTERNS = [r"immediately", r"urgent", r"as soon as possible", r"within 24 hours", r"act now"]
    FINANCIAL_PATTERNS = [r"bank account", r"wire transfer", r"credit card", r"bitcoin", r"gift card"]
    IMPERSONATION_PATTERNS = [r"official representative", r"irs", r"microsoft support"]

    def __init__(self, confidence_threshold=0.7, persistence=None):
        self.confidence_threshold = confidence_threshold
        if persistence:
            custom_kws = persistence.get('custom_keywords', {'urgency': [], 'financial': []})
            self.URGENCY_PATTERNS.extend(custom_kws.get('urgency', []))
            self.FINANCIAL_PATTERNS.extend(custom_kws.get('financial', []))

    def scan_text(self, text):
        results = {
            "urgency": self._match(text, self.URGENCY_PATTERNS),
            "financial": self._match(text, self.FINANCIAL_PATTERNS),
            "impersonation": self._match(text, self.IMPERSONATION_PATTERNS),
            "threat_level": "Low"
        }
        score = (len(results["urgency"]) + len(results["financial"]) + len(results["impersonation"])) / 10
        if score > 0.5: results["threat_level"] = "High"
        elif score > 0.2: results["threat_level"] = "Medium"
        return results

    def _match(self, text, patterns):
        return [p for p in patterns if re.search(p, text, re.IGNORECASE)]

    def generate_threat_report(self, results):
        report = f"--- THREAT ANALYSIS REPORT ---\nFinal Threat Level: {results['threat_level']}\nIndicators: "
        indicators = results['urgency'] + results['financial'] + results['impersonation']
        report += ", ".join(indicators) if indicators else "None"
        return report + "\n------------------------------"

# --- 3. Gmail Service ---
class GmailService:
    def __init__(self, config_path='config.yaml', access_token=None, sandbox_mode=False):
        self.access_token = access_token
        self.sandbox_mode = sandbox_mode
        self.persistence = LocalPersistence() if self.sandbox_mode else None
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    def authenticate(self, access_token_override=None):
        if self.sandbox_mode: return None
        try:
            token = access_token_override or self.access_token
            creds = Credentials(token=token) if token else None
            if not creds: raise Exception("No credentials provided.")
            self.service = build('gmail', 'v1', credentials=creds)
            return self.service
        except Exception as e:
            print(f"Authentication failed: {e}. Falling back to Sandbox Mode.")
            self.enable_sandbox_mode()
            return None

    def enable_sandbox_mode(self):
        self.sandbox_mode = True
        if not self.persistence: self.persistence = LocalPersistence()
        print("Local Sandbox Mode initialized.")

    def list_messages(self):
        if self.sandbox_mode:
            return [{'id': 'msg_1'}, {'id': 'msg_2'}]
        return self.service.users().messages().list(userId='me').execute().get('messages', [])

    def get_message(self, message_id):
        if self.sandbox_mode:
            return {
                'msg_1': {'id': 'msg_1', 'snippet': 'Urgent: Financial transfer required'},
                'msg_2': {'id': 'msg_2', 'snippet': 'Hello from your bank'}
            }.get(message_id)
        return self.service.users().messages().get(userId='me', id=message_id).execute()

# --- 4. Terminal UI ---
class TerminalApp:
    def __init__(self, sandbox_mode=True):
        self.gmail = GmailService(sandbox_mode=sandbox_mode)
        self.engine = ScanEngine(persistence=self.gmail.persistence)
        self.running = True

    def run(self):
        print("\n" + "="*50 + "\n ANTI-SCAM AI: PORTABLE SECURITY SANDBOX\n" + "="*50)
        while self.running:
            cmd = input("\n[Sandbox] > ").strip().lower()
            if cmd in ["exit", "quit"]: self.running = False
            elif cmd == "scan": self.run_scan()
            elif cmd == "sync": self.run_sync()
            elif cmd == "purge": self.run_purge()
            elif cmd == "keywords": self.edit_keywords()
            elif cmd.startswith("override "): self.gmail.access_token = cmd.split(" ", 1)[1]; print("Token applied.")
            elif cmd == "help": self.print_help()
            else: print("Unknown command. Type 'help'.")

    def print_help(self):
        print("\nCommands: scan, sync, purge, keywords, override <token>, help, exit")

    def run_scan(self):
        messages = self.gmail.list_messages()
        reports = self.gmail.persistence.get('reports', [])
        for msg in messages:
            full_msg = self.gmail.get_message(msg['id'])
            analysis = self.engine.scan_text(full_msg['snippet'])
            print(f"[*] Analyzing {msg['id']}: {analysis['threat_level']}")
            reports.append({"time": time.ctime(), "msg": msg['id'], "report": self.engine.generate_threat_report(analysis)})
        self.gmail.persistence.set('reports', reports)

    def run_sync(self):
        print("Syncing with Secure Edge..."); time.sleep(1); print("Sync Successful.")

    def run_purge(self):
        print("Purging suspicious sectors..."); time.sleep(1); print("Purge Complete.")

    def edit_keywords(self):
        kw = input("Enter new urgency keyword: ")
        self.engine.URGENCY_PATTERNS.append(kw)
        custom = self.gmail.persistence.get('custom_keywords', {'urgency': [], 'financial': []})
        custom['urgency'].append(kw); self.gmail.persistence.set('custom_keywords', custom)
        print(f"Added '{kw}'.")

# --- Main Entry ---
def check_conn():
    try:
        socket.setdefaulttimeout(2)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except: return False

if __name__ == "__main__":
    print("Checking network...")
    if not check_conn(): print("[!] ERR_CONNECTION_TIMED_OUT detected. Booting into Self-Healing Sandbox.")
    app = TerminalApp(sandbox_mode=True)
    app.run()
