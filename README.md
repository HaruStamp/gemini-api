# Media Generation API Powered by Gemini AI

Media generation API for speech, image, video, and music powered by Google Gemini AI. Built with Flask.

## 📡 API – Endpoint

### 🗣️ Speech Generation

Generate realistic text-to-speech audio using Google Gemini TTS Model via `/api/gen/speech`

Endpoint:
```bash
POST /api/gen/speech
```

Request Body (JSON):
```bash
{
  "model": "gemini-2.5-flash-preview-tts",
  "contents": "Speaker1: Hello! It's nice to meet you.\nSpeaker2: Hi! Nice to meet you too. How are you today?\nSpeaker1: I'm doing great, thanks. What about you?\nSpeaker2: I'm good too. Just finished some work.",
  "config": {
    "response_modalities": ["AUDIO"],
    "speech_config": {
      "multi_speaker_voice_config": {
        "speaker_voice_configs": [
          {
            "speaker": "Speaker1",
            "voice_config": {
              "prebuilt_voice_config": {
                "voice_name": "Zephyr"
              }
            }
          },
          {
            "speaker": "Speaker2",
            "voice_config": {
              "prebuilt_voice_config": {
                "voice_name": "Puck"
              }
            }
          }
        ]
      }
    }
  }
}
```

---

## ⚙️ Server Setup Guide

### ✅ Prerequisites

- Ubuntu 22.04 (LTS)
- Root or sudo privileges
- Internet connection

### Step 1: Configure Firewall (UFW)

```bash
sudo ufw limit ssh
sudo ufw enable
sudo ufw status
```

### Step 2: Install Essential Packages

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv
```

Check versions to confirm installation:
```bash
git --version
python3 --version
pip3 --version
```

### 🧩 Step 3: Clone Project & Setup Python Environment

Clone the repository and navigate into the API folder:
```bash
cd /opt
sudo git clone https://github.com/HaruStamp/gemini-api.git media-gen
cd media-gen/api
```

Create a Python virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Create .env File

The project uses environment variables to securely load API keys.

Create a .env file inside /opt/media-gen/api:
```bash
nano .env
```

Paste the following configuration:
```bash
GEMINI_API_KEY=your_google_genai_api_key
```
Save and exit (Ctrl + O, then Enter, and Ctrl + X).

### Step 5: Configure Gunicorn with systemd

Gunicorn will serve the app using the existing wsgi.py file in the repo.

Create a systemd service file:
```bash
cat <<EOF | sudo tee /etc/systemd/system/gunicorn.service > /dev/null
[Unit]
Description=Media  API
After=network.target

[Service]
User=root
WorkingDirectory=/opt/media-gen/api
Environment="PATH=/opt/media-gen/api/venv/bin"
ExecStart=/opt/media-gen/api/venv/bin/gunicorn -w 3 -b 0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

Start and Enable Gunicorn Service:
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

Check status:
```bash
sudo systemctl status gunicorn
```
You should see a status like: Active: active (running)

### Step 6: Verify Server is Running

After starting Gunicorn, test the server using:
```bash
curl http://localhost:5000
```

You should see:
```bash
✅ Media Generation API is running.
```

---

## 🛠 Recommended Directory Structure

Your project folder should look like this after setup:

```bash
/opt/media-gen
├── api
│   ├── app.py
│   ├── wsgi.py
│   ├── requirements.txt
│   ├── .env
│   ├── venv/
│   ├── routes/
│   └── utils/
```

---

## 🌐 Connecting Domain & Enabling HTTPS with NGINX + Certbot (Optional)

This guide helps you secure your Media Generation API with HTTPS using NGINX and Let's Encrypt (Certbot).  
It assumes the API is already running on port `5000` via Docker or directly on the host.


### ✅ Prerequisites

- A domain name (e.g. `api.yourdomain.com`)
- A DNS A-record pointing to your server’s public IP
- Media Generation API must be accessible at `http://localhost:5000`
- Port 80 and 443 are **open** on the server (`ufw allow 'Nginx Full'`)

### Step 1: Install NGINX and Certbot

```bash
apt update
apt install -y nginx certbot python3-certbot-nginx
```

### STEP 2: Allow HTTP and HTTPS in UFW Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### STEP 3: Prepare Webroot Path for Certbot

```bash
sudo mkdir -p /var/www/certbot/.well-known/acme-challenge
```

### STEP 4: Create NGINX Config

```bash
nano /etc/nginx/sites-available/media-gen-api
```

Paste the following configuration:

```bash
server {
    listen 80;
    server_name api.example.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Save and exit (Ctrl + O, then Enter, and Ctrl + X).

Test the NGINX configuration:

```bash
sudo ln -s /etc/nginx/sites-available/media-gen-api /etc/nginx/sites-enabled/media-gen-api
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
```

If the test passes, reload NGINX:

```bash
sudo systemctl reload nginx
```

### STEP 5: Obtain SSL Certificate (Let’s Encrypt)

Generate the certificate:

```bash
sudo certbot --nginx -d api.example.com
```

**You should see a message like:**

```bash
Successfully received certificate.
```

### STEP 6: Verify HTTPS is Working

```bash
curl https://api.example.com --insecure
```

You should see:

```bash
✅ Media Generation API is running.
```

##### STEP 7: Verify Auto-Renewal (Optional)

Certbot configures auto-renew automatically. To confirm:

```bash
sudo systemctl list-timers | grep certbot
```

To manually test auto-renew:

```bash
sudo certbot renew --dry-run
```

---

## ✅ Final Checklist

Before deploying, make sure:

- [ ] Project was cloned into `/opt/media-gen`
- [ ] Python environment and dependencies installed in `/opt/media-gen/api/venv`
- [ ] `.env` file created with valid `GEMINI_API_KEY`
- [ ] Gunicorn is active and serving `wsgi:app`
- [ ] HTTPS via NGINX + Certbot is working at `https://api.yourdomain.com`

You’re now ready to scale your AI-powered media generation service 🚀

---

