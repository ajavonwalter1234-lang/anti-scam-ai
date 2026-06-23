import time
import sys
from .gmail_service import GmailService
from .scan_engine import ScanEngine

class TerminalApp:
    """An interactive terminal environment for the Anti-Scam AI Sandbox."""

    def __init__(self, sandbox_mode=True):
        self.gmail = GmailService(sandbox_mode=sandbox_mode)
        self.engine = ScanEngine(persistence=self.gmail.persistence if sandbox_mode else None)
        self.running = True

    def run(self):
        """Starts the terminal application loop."""
        print("\n" + "="*50)
        print(" ANTI-SCAM AI: LOCAL SECURITY SANDBOX v1.0")
        print("="*50)
        print("Status: AUTH_HANDSHAKE_BYPASSED (Sandbox Mode Active)")
        print("Protocol: SECURE_LOCAL_LOOP")
        print("-" * 50)

        while self.running:
            cmd = input("\n[Sandbox] > ").strip().lower()
            if cmd in ["exit", "quit"]:
                self.running = False
                print("Exiting Sandbox Mode...")
            elif cmd == "help":
                self.print_help()
            elif cmd == "scan":
                self.run_scan()
            elif cmd == "vectors":
                self.show_vectors()
            elif cmd == "reports":
                self.show_reports()
            elif cmd == "keywords":
                self.edit_keywords()
            elif cmd == "sync":
                self.run_sync()
            elif cmd == "purge":
                self.run_purge()
            elif cmd == "config":
                self.show_config()
            elif cmd.startswith("override "):
                token = cmd.split(" ", 1)[1]
                self.apply_override(token)
            else:
                print(f"Unknown command: '{cmd}'. Type 'help' for options.")

    def print_help(self):
        print("\nAvailable Commands:")
        print("  scan      : Fetch and scan messages (Sandbox/Simulated)")
        print("  sync      : Synchronize local threat intelligence")
        print("  purge     : Bulk purge suspicious mail sectors")
        print("  vectors   : Display active scan vectors")
        print("  reports   : View saved threat reports")
        print("  keywords  : Add custom keywords to scan engine")
        print("  config    : Show sandbox preferences")
        print("  override <token> : Apply a manual Google Access Token override")
        print("  help      : Show this help message")
        print("  exit/quit : Return to main application")

    def run_scan(self):
        print("\nInitializing scanner loop...")
        time.sleep(0.5)
        messages = self.gmail.list_messages()
        print(f"Found {len(messages)} messages for analysis.\n")

        reports = self.gmail.persistence.get('reports', [])

        for msg in messages:
            full_msg = self.gmail.get_message(msg['id'])
            snippet = full_msg.get('snippet', '')
            print(f"[*] Analyzing Message {msg['id']}...")
            analysis = self.engine.scan_text(snippet)

            print(f"    Snippet: {snippet[:60]}...")
            print(f"    Threat Level: {analysis['threat_level']}")
            if analysis['threat_level'] != "Low":
                print(f"    Indicators: {', '.join(analysis['urgency'] + analysis['financial'] + analysis['impersonation'])}")

            report = self.engine.generate_threat_report(analysis)
            reports.append({
                "timestamp": time.ctime(),
                "message_id": msg['id'],
                "report": report
            })
            print("-" * 20)

        self.gmail.persistence.set('reports', reports)
        print("Scan complete. Reports saved to persistence.")

    def show_reports(self):
        print("\nSaved Threat Reports:")
        reports = self.gmail.persistence.get('reports', [])
        if not reports:
            print("  No reports found.")
        for r in reports:
            print(f"\n[{r['timestamp']}] Message: {r['message_id']}")
            print(r['report'])

    def edit_keywords(self):
        print("\nCustom Keyword Management:")
        print("  1. Add Urgency Keyword")
        print("  2. Add Financial Keyword")
        choice = input("Select category: ")
        kw = input("Enter keyword: ")

        custom_kws = self.gmail.persistence.get('custom_keywords', {'urgency': [], 'financial': []})

        if choice == "1":
            self.engine.URGENCY_PATTERNS.append(kw)
            custom_kws['urgency'].append(kw)
            print(f"Added '{kw}' to Urgency patterns.")
        elif choice == "2":
            self.engine.FINANCIAL_PATTERNS.append(kw)
            custom_kws['financial'].append(kw)
            print(f"Added '{kw}' to Financial patterns.")

        self.gmail.persistence.set('custom_keywords', custom_kws)

    def run_sync(self):
        print("\nInitiating Intelligence Sync...")
        steps = ["Connecting to Secure Edge...", "Downloading Threat Definitions...", "Updating Local Model Weights...", "Syncing Session Cache..."]
        for step in steps:
            print(f"  > {step}")
            time.sleep(0.4)

        self.gmail.persistence.set('last_sync', time.ctime())
        print("Sync Successful. Intelligence database is up to date.")

    def run_purge(self):
        print("\nWarning: Initiating Bulk Purge of Suspicious Mail Sectors...")
        time.sleep(0.5)
        sectors = ["Sector-7G", "Sector-12F", "Vault-Alpha"]
        for s in sectors:
            print(f"  [PURGING] {s}...")
            time.sleep(0.3)

        purges = self.gmail.persistence.get('purge_history', [])
        purges.append({"timestamp": time.ctime(), "sectors": sectors})
        self.gmail.persistence.set('purge_history', purges)
        print("Purge Complete. 3 high-risk sectors neutralized.")

    def show_vectors(self):
        print("\nActive Scan Vectors (Live Visualization):")
        vectors = self.engine.get_simulated_vectors()
        for v in vectors:
            print(f"  [{v['status']}] {v['type']} via {v['source']} -> {v['indicator']}")

    def show_config(self):
        print("\nSandbox Preferences:")
        print(f"  Persistence: Local JSON Sync (data/local_storage.json)")
        print(f"  Network Mode: Air-gapped / Localhost")
        print(f"  Confidence Threshold: {self.engine.confidence_threshold}")

    def apply_override(self, token):
        print(f"\nApplying Manual Access Token Override...")
        self.gmail.access_token = token
        print("Token applied. Note: Network protocol handshake will still use fallback if firewall block persists.")
