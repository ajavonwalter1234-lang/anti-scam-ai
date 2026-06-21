import re

class ScanEngine:
    """Engine for detecting scams in text and speech data."""

    URGENCY_PATTERNS = [
        r"immediately", r"urgent", r"as soon as possible", r"within 24 hours",
        r"limited time", r"final notice", r"act now", r"emergency"
    ]

    FINANCIAL_PATTERNS = [
        r"bank account", r"wire transfer", r"credit card", r"ssn", r"social security",
        r"password", r"routing number", r"bitcoin", r"crypto", r"gift card"
    ]

    IMPERSONATION_PATTERNS = [
        r"official representative", r"irs", r"microsoft support", r"amazon security",
        r"police department", r"government agency"
    ]

    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold

    def scan_text(self, text):
        """Analyzes text for scam indicators."""
        results = {
            "urgency": self._match_patterns(text, self.URGENCY_PATTERNS),
            "financial": self._match_patterns(text, self.FINANCIAL_PATTERNS),
            "impersonation": self._match_patterns(text, self.IMPERSONATION_PATTERNS),
            "threat_level": "Low"
        }

        score = (len(results["urgency"]) + len(results["financial"]) + len(results["impersonation"])) / 10
        if score > 0.5:
            results["threat_level"] = "High"
        elif score > 0.2:
            results["threat_level"] = "Medium"

        return results

    def _match_patterns(self, text, patterns):
        """Helper to find matches for a list of patterns."""
        matches = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        return matches

    def get_simulated_vectors(self):
        """Returns simulated scan vectors for Sandbox Mode."""
        return [
            {"type": "Text", "source": "Email", "indicator": "Urgency", "status": "Detected"},
            {"type": "Speech", "source": "Voice Call", "indicator": "Stress", "status": "Monitoring"},
            {"type": "Network", "source": "IP Trace", "indicator": "Suspicious VPN", "status": "Flagged"}
        ]

    def generate_threat_report(self, results):
        """Generates a summary report of findings."""
        report = "--- THREAT ANALYSIS REPORT ---\n"
        report += f"Final Threat Level: {results['threat_level']}\n"
        report += "Indicators Found:\n"
        for key in ['urgency', 'financial', 'impersonation']:
            if results[key]:
                report += f"  - {key.capitalize()}: {', '.join(results[key])}\n"
        if not any(results[key] for key in ['urgency', 'financial', 'impersonation']):
            report += "  - None detected.\n"
        report += "------------------------------"
        return report
