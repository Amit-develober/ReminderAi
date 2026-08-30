# 🌅 PulseAI — 8:00 AM WhatsApp Morning Briefing & Web Subscription Portal

An automated, executive-grade AI morning intelligence chief-of-staff. It compiles real-time weather, top industry news, and community trends tailored to each subscriber's selected niche, synthesizes a bite-sized 20-second summary using **Google Gemini AI**, and delivers it to **WhatsApp** every morning at **8:00 AM**.

Includes a **modern web subscription portal** where users can enter their mobile number, pick their topics/niches, and receive personalized daily briefs.

---

## ✨ Features
- 🌐 **Interactive Subscription Webpage**: Users can choose their name, phone, city, and select multiple niche topics (AI, Startups, Crypto, Biotech, Cyber, etc.) with real-time live WhatsApp message preview.
- 👥 **Multi-Subscriber Personalized Pipeline**: Generates unique, customized briefings based on each subscriber's chosen niche topics and local city weather.
- 💬 **Reliable WhatsApp Delivery**: Sends link-free, bite-sized bullet points via **Green API** (or Twilio Sandbox / Meta Cloud API).
- ⏰ **Automated 8:00 AM Delivery via GitHub Actions**: Runs completely free 24/7 in the cloud without keeping your PC powered on.
- ⚡ **Instant Test Dispatch**: Users on the web portal can hit "Send Me a Sample Now" to receive a test briefing immediately.

---

## 🚀 How to Run the Web Subscription Portal Locally

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Web Portal**:
   ```bash
   python web_app.py
   ```
3. Open your browser to: **`http://127.0.0.1:5000`**
   - Enter your name, WhatsApp number, city, and select your niches.
   - Click **"Subscribe for 8:00 AM Daily Brief"** or **"Send Me a Sample Now"**.

---

## ☁️ How to Automate 24/7 on GitHub Actions (8:00 AM Every Day)

You don't need to keep your computer turned on! GitHub Actions will run this pipeline automatically every morning.

### Step 1: Push this Project to GitHub
1. Create a **Private Repository** on GitHub (e.g. `whatsapp-daily-briefing`).
2. Push your project code:
   ```bash
   git init
   git add .
   git commit -m "PulseAI WhatsApp daily briefing bot and web portal"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

### Step 2: Add Repository Secrets on GitHub
1. In your GitHub repository, navigate to **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
2. Click **"New repository secret"** and add:
   - `GEMINI_API_KEY`: Your Gemini API key from [Google AI Studio](https://aistudio.google.com/)
   - `GREEN_API_INSTANCE_ID`: `710722723355`
   - `GREEN_API_TOKEN`: `2b0834d826584d5c86160f385103bccbf7d2d4bec8cc49a3a3`
   - `WHATSAPP_PHONE`: `+917838736976`

3. (Optional) Under **Variables**, you can customize:
   - `NOTIFICATION_CHANNEL`: `whatsapp`
   - `WHATSAPP_PROVIDER`: `green_api`

### Step 3: Trigger a Manual Test Run on GitHub
1. Go to the **Actions** tab on your GitHub repository.
2. Select **"Daily AI Briefing Bot (8:00 AM WhatsApp)"** on the left menu.
3. Click **"Run workflow"** $\rightarrow$ **"Run workflow"**.
4. GitHub Actions will execute the runner and dispatch the message to WhatsApp!

---

## 🛠️ Project Structure

```
├── .github/workflows/
│   └── daily_briefing.yml    # GitHub Actions 24/7 cloud scheduler (8:00 AM IST)
├── templates/
│   └── index.html            # Subscription landing page with live simulation
├── static/
│   ├── style.css             # Glassmorphism dark-mode styling
│   └── app.js                # Dynamic live preview & subscription AJAX logic
├── notifiers/
│   ├── whatsapp_notifier.py  # Green API, Twilio & Meta Cloud API dispatchers
│   └── telegram_notifier.py  # Telegram Bot API dispatcher
├── sources/
│   ├── weather.py            # Open-Meteo real-time weather integration
│   └── news.py               # RSS feeds & community trends collector
├── subscribers.py            # Subscriber database manager
├── subscribers.json          # Active subscribers list
├── ai_summarizer.py          # Gemini AI executive briefing prompt engine
├── config.py                 # Settings & environment validation
├── main.py                   # CLI & multi-subscriber batch runner
├── web_app.py                # Web server for public subscription portal
├── requirements.txt          # Python dependencies
├── .env.example              # Template environment variables
└── README.md                 # Complete documentation
```


