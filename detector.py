"""
Phishing Detection Engine
Analyses URLs and email text for phishing indicators.
"""

import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional


# ─── Known Indicators ────────────────────────────────────────────────────────

SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club",
    ".online", ".site", ".info", ".biz", ".icu", ".cam"
}

TRUSTED_BRANDS = [
    "paypal", "amazon", "google", "microsoft", "apple", "facebook",
    "instagram", "netflix", "linkedin", "twitter", "dropbox", "bank",
    "chase", "wellsfargo", "hsbc", "barclays", "ebay", "steam"
]

URGENT_PHRASES = [
    "verify your account", "confirm your identity", "your account has been",
    "suspended", "limited", "unusual activity", "click here immediately",
    "act now", "expires in", "validate your", "update your information",
    "you have won", "congratulations", "claim your prize", "urgent action",
    "account will be closed", "locked", "unauthorized access", "login attempt",
    "security alert", "immediately", "within 24 hours", "as soon as possible",
    "failure to", "we noticed", "verify now", "click below to confirm"
]

DECEPTIVE_KEYWORDS = [
    "login", "signin", "sign-in", "secure", "account", "update",
    "verify", "confirm", "banking", "password", "credential", "wallet",
    "webscr", "ebayisapi", "authenticate", "validation"
]

KNOWN_PHISHING_PATTERNS = [
    r"paypa[l1]",
    r"app[l1]e",
    r"micro\$oft",
    r"g[o0]{2}g[l1]e",
    r"amaz[o0]n",
    r"faceb[o0]{2}k",
    r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}",  # Raw IP address
]


# ─── Result Model ─────────────────────────────────────────────────────────────

@dataclass
class AnalysisResult:
    input_value: str
    input_type: str  # 'url' or 'email'
    risk_score: int = 0         # 0–100
    risk_level: str = "Safe"    # Safe / Low / Medium / High / Critical
    flags: list = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def compute_risk_level(self):
        if self.risk_score >= 80:
            self.risk_level = "Critical"
        elif self.risk_score >= 60:
            self.risk_level = "High"
        elif self.risk_score >= 35:
            self.risk_level = "Medium"
        elif self.risk_score >= 15:
            self.risk_level = "Low"
        else:
            self.risk_level = "Safe"


# ─── URL Analyser ─────────────────────────────────────────────────────────────

def analyse_url(url: str) -> AnalysisResult:
    result = AnalysisResult(input_value=url, input_type="url")

    # Ensure URL has a scheme for parsing
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        parsed = urllib.parse.urlparse(url)
        hostname = parsed.hostname or ""
        path = parsed.path.lower()
        full_url = url.lower()
    except Exception:
        result.flags.append("Could not parse URL")
        result.risk_score = 50
        result.compute_risk_level()
        return result

    # 1. HTTP vs HTTPS
    if parsed.scheme == "http":
        result.flags.append("Uses insecure HTTP (not HTTPS)")
        result.risk_score += 10

    # 2. IP address as host
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
        result.flags.append("Uses raw IP address instead of a domain name")
        result.risk_score += 25

    # 3. Suspicious TLD
    for tld in SUSPICIOUS_TLDS:
        if hostname.endswith(tld):
            result.flags.append(f"Suspicious top-level domain: {tld}")
            result.risk_score += 20
            break

    # 4. Brand impersonation in subdomain/path
    for brand in TRUSTED_BRANDS:
        if brand in hostname and not hostname.endswith(f"{brand}.com"):
            result.flags.append(f"Possible brand impersonation: '{brand}' in URL but not official domain")
            result.risk_score += 30
            break

    # 5. Typosquatting / leet-speak patterns
    for pattern in KNOWN_PHISHING_PATTERNS:
        if re.search(pattern, full_url):
            result.flags.append(f"Typosquatting or lookalike pattern detected")
            result.risk_score += 20
            break

    # 6. Excessive subdomains
    subdomain_count = hostname.count(".")
    if subdomain_count >= 3:
        result.flags.append(f"Excessive subdomains ({subdomain_count} dots) — common in phishing URLs")
        result.risk_score += 15

    # 7. URL length
    if len(url) > 75:
        result.flags.append(f"Unusually long URL ({len(url)} characters)")
        result.risk_score += 10

    # 8. Deceptive keywords in path
    found_keywords = [kw for kw in DECEPTIVE_KEYWORDS if kw in path or kw in full_url]
    if found_keywords:
        result.flags.append(f"Suspicious keywords in URL: {', '.join(found_keywords[:3])}")
        result.risk_score += 15

    # 9. URL contains @ symbol (tricks browsers)
    if "@" in url:
        result.flags.append("URL contains '@' — can be used to obscure the real destination")
        result.risk_score += 20

    # 10. Multiple redirects / double slashes in path
    if "//" in path:
        result.flags.append("Double slashes in path — possible redirect trick")
        result.risk_score += 10

    # 11. Hyphenated domain (common in phishing)
    domain_parts = hostname.split(".")
    if any("-" in part for part in domain_parts[:-1]):
        result.flags.append("Hyphenated domain name — frequently used in phishing")
        result.risk_score += 10

    result.details = {
        "hostname": hostname,
        "scheme": parsed.scheme,
        "path": parsed.path,
        "url_length": len(url),
    }

    result.risk_score = min(result.risk_score, 100)
    result.compute_risk_level()
    return result


# ─── Email Analyser ───────────────────────────────────────────────────────────

def analyse_email(email_text: str) -> AnalysisResult:
    result = AnalysisResult(input_value=email_text[:80] + "..." if len(email_text) > 80 else email_text,
                            input_type="email")

    text_lower = email_text.lower()

    # 1. Urgent / threatening language
    found_urgent = [phrase for phrase in URGENT_PHRASES if phrase in text_lower]
    if found_urgent:
        result.flags.append(f"Urgent/threatening language detected: \"{found_urgent[0]}\"")
        result.risk_score += min(len(found_urgent) * 10, 40)

    # 2. URLs embedded in email
    urls_found = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', email_text)
    if urls_found:
        result.details["embedded_urls"] = urls_found
        result.flags.append(f"{len(urls_found)} embedded URL(s) found — verify each carefully")
        result.risk_score += 10

        # Check each embedded URL
        for url in urls_found[:3]:
            url_result = analyse_url(url)
            if url_result.risk_level in ("High", "Critical"):
                result.flags.append(f"Embedded URL flagged as {url_result.risk_level} risk: {url[:50]}")
                result.risk_score += 20

    # 3. Mismatched sender (looking for "From:" vs domain)
    from_match = re.search(r'from:\s*(.+)', text_lower)
    if from_match:
        from_line = from_match.group(1)
        for brand in TRUSTED_BRANDS:
            if brand in from_line:
                domain_match = re.search(r'@([\w.-]+)', from_line)
                if domain_match:
                    sender_domain = domain_match.group(1)
                    if brand not in sender_domain:
                        result.flags.append(
                            f"Sender claims to be '{brand}' but email domain is '{sender_domain}'"
                        )
                        result.risk_score += 35

    # 4. Generic greeting
    if re.search(r'\bdear (customer|user|member|account holder|valued)\b', text_lower):
        result.flags.append("Generic greeting used — legitimate companies use your real name")
        result.risk_score += 10

    # 5. Requests for sensitive info
    sensitive_requests = ["password", "credit card", "social security", "ssn",
                          "bank account", "pin", "mother's maiden", "date of birth"]
    found_sensitive = [s for s in sensitive_requests if s in text_lower]
    if found_sensitive:
        result.flags.append(f"Requests sensitive information: {', '.join(found_sensitive)}")
        result.risk_score += 30

    # 6. Spelling / grammar issues (simple heuristic)
    common_errors = ["recieve", "verfiy", "acount", "informtion", "securty",
                     "pasword", "clik", "acount", "vaildate", "suspisious"]
    found_errors = [e for e in common_errors if e in text_lower]
    if found_errors:
        result.flags.append(f"Possible spelling errors detected — common in phishing emails")
        result.risk_score += 15

    # 7. Attachments mentioned
    if re.search(r'\b(attachment|attached|open the file|download the|click to open)\b', text_lower):
        result.flags.append("Mentions attachments or file downloads — exercise caution")
        result.risk_score += 15

    result.details["word_count"] = len(email_text.split())
    result.details["urgent_phrases_found"] = len(found_urgent)

    result.risk_score = min(result.risk_score, 100)
    result.compute_risk_level()
    return result


# ─── Auto-detect & Route ──────────────────────────────────────────────────────

def analyse(text: str) -> AnalysisResult:
    """Auto-detect whether input is a URL or email body and analyse accordingly."""
    stripped = text.strip()
    if re.match(r'^(https?://|www\.)\S+$', stripped) or re.match(r'^[\w.-]+\.[a-z]{2,}(/\S*)?$', stripped):
        return analyse_url(stripped)
    else:
        return analyse_email(stripped)


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json

    print("=" * 60)
    print("  PHISHING DETECTION TOOL")
    print("  Paste a URL or email body to analyse.")
    print("  Type 'quit' to exit.")
    print("=" * 60)

    while True:
        print()
        user_input = input(">>> ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue

        result = analyse(user_input)

        print(f"\n  Input Type  : {result.input_type.upper()}")
        print(f"  Risk Score  : {result.risk_score}/100")
        print(f"  Risk Level  : {result.risk_level}")
        if result.flags:
            print(f"\n  Flags Raised:")
            for flag in result.flags:
                print(f"    ⚠  {flag}")
        else:
            print("\n  ✓ No suspicious indicators found.")
        print()
