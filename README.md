# PhishGuard — Phishing Detection Tool

A Python-based phishing detection tool that analyses URLs and email content
for suspicious indicators. Includes a CLI script and a Flask web app.

---

## Features

- **URL Analysis** — Detects suspicious TLDs, IP-based URLs, brand impersonation,
  typosquatting, excessive subdomains, deceptive keywords, and more
- **Email Analysis** — Flags urgent language, mismatched senders, sensitive data
  requests, embedded phishing URLs, and common spelling tricks
- **Risk Scoring** — Each scan returns a 0–100 risk score and a risk level:
  Safe / Low / Medium / High / Critical
- **Web UI** — Clean dark-themed interface built with Flask + vanilla JS

---

## Project Structure

```
phishing-detector/
├── detector.py        # Core detection engine (import or run standalone)
├── app.py             # Flask web application
├── requirements.txt   # Python dependencies
├── templates/
│   └── index.html     # Web UI
└── README.md
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the web app
```bash
python app.py
```
Then open your browser at: **http://localhost:5000**

### 3. Run the CLI (no Flask needed)
```bash
python detector.py
```
Then paste any URL or email body at the prompt.

---

## How It Works

### URL Checks
| Check | Score Added |
|---|---|
| Uses HTTP instead of HTTPS | +10 |
| Raw IP address as host | +25 |
| Suspicious TLD (.tk, .ml, .xyz…) | +20 |
| Brand impersonation in URL | +30 |
| Typosquatting / leet-speak patterns | +20 |
| Excessive subdomains | +15 |
| Unusually long URL | +10 |
| Deceptive keywords in path | +15 |
| @ symbol in URL | +20 |
| Hyphenated domain name | +10 |

### Email Checks
| Check | Score Added |
|---|---|
| Urgent / threatening language | up to +40 |
| Embedded phishing URLs | +20 per URL |
| Mismatched sender domain | +35 |
| Generic greeting (Dear Customer) | +10 |
| Requests for sensitive info | +30 |
| Spelling/grammar errors | +15 |
| Mentions attachments | +15 |

---

## Example Test Inputs

**Phishing URL:**
```
http://paypa1-secure-verify.tk/login?ref=account&update=true
```

**Safe URL:**
```
https://www.google.com/search?q=cybersecurity
```

**Phishing Email:**
```
From: security@paypa1-support.com

Dear Customer,

We have detected unusual activity on your account. Your account will be 
suspended within 24 hours unless you verify your account immediately.

Click here: http://paypa1-verify.ml/secure-login

Failure to act now will result in permanent account closure.
```

---

## Possible Extensions (to strengthen your CV)

- [ ] Integrate VirusTotal or Google Safe Browsing API for live URL lookup
- [ ] Add a machine learning classifier (scikit-learn) trained on a phishing dataset
- [ ] Browser extension wrapper
- [ ] Email header parser (`.eml` file support)
- [ ] Export scan report as PDF

---

## Technologies Used
- Python 3.10+
- Flask 2.3+
- HTML / CSS / JavaScript (vanilla)

---

*Built as a final year cybersecurity project. For educational purposes only.*
