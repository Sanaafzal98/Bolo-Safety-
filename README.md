# Bolo Safety — Voice HSE Observation App

Flask app: workers record a safety observation **in Urdu**, it's automatically
transcribed, translated to English, categorized (Unsafe Act / Unsafe Condition /
Near Miss / LTI + severity + location), the audio is saved to Google Drive, and
everything shows up live on HSE and Admin dashboards (charts + log + filters),
exactly like the sample "Bolo Safety Overview" you shared.

## 3 panels
- **User** — see their own submissions. Recording no longer happens in the browser — it comes
  from the external voice recorder (ASR) app via webhook (see below).
- **HSE** — full analytics dashboard (all reporters), can edit category/severity/location/status.
- **Admin** — everything HSE has, **plus** full CRUD (add/edit/delete any observation, delete audio),
  and user management (create/delete admin, hse, user accounts).

## Voice webhook (external ASR / recorder app)
Your recorder app posts the raw audio file straight to this backend — no recording UI in the
dashboard anymore. This server then runs the exact same Groq pipeline as before (auto-detects the
spoken language, transcribes it, translates to English, and extracts category/severity/location),
and the result appears live on the User/HSE/Admin dashboards.

```
POST /api/webhook/voice-observation
Headers:  X-Webhook-Key: <WEBHOOK_API_KEY from .env>
Body (multipart/form-data):
  audio            — required, the recorded audio file
  username         — optional, must match an existing account's username to link the report to it
  reporter_name    — optional, used as a fallback name if the audio itself doesn't mention one
```

Response: `201` with the saved observation as JSON, or `401`/`400`/`500` with an `error` message.

Set `WEBHOOK_API_KEY` in `.env` to any long random string and configure the same value in the
recorder app. Leave it blank only for local testing.

## 1. Install

```bash
cd safety-app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure environment

```bash
cp .env.example .env
```
Then edit `.env`:
- `GROQ_API_KEY` — free key from https://console.groq.com/keys (this powers transcription,
  translation, and categorization — `whisper-large-v3` + `llama-3.3-70b-versatile`).
- Google Drive (optional, see below) — if you skip this, audio is still saved locally
  in `/uploads` and everything else works normally.

### Google Drive setup (optional but requested)
1. Go to https://console.cloud.google.com → create a project → enable **Google Drive API**.
2. **APIs & Services → Credentials → Create Credentials → Service Account** → create a JSON key.
3. Save that JSON file as `service_account.json` in the project root.
4. In Google Drive, create a folder for reports, right-click → **Share** → paste the
   service account's email (looks like `xxx@xxx.iam.gserviceaccount.com`) with **Editor** access.
5. Copy the folder ID from its URL (`drive.google.com/drive/folders/<THIS_PART>`) into
   `GOOGLE_DRIVE_FOLDER_ID` in `.env`.

## 3. Initialize the database (creates demo users)

```bash
flask --app app.py init-db
```
This creates:
| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | admin    | admin123  |
| HSE   | hse      | hse123    |
| User  | worker   | worker123 |

**Change these passwords / delete these accounts before going live.**

## 4. Run

```bash
python app.py
```
Open http://localhost:5000

## How the AI pipeline works (`groq_service.py`)
1. `whisper-large-v3` (transcription endpoint, language auto-detected — Urdu or any other
   language) → original-language script.
2. `whisper-large-v3` (translation endpoint) → **English translation** of the audio.
3. `llama-3.3-70b-versatile` reads the English translation and returns strict JSON:
   `category`, `severity`, `location`, `reporter_name`, `summary` — this is what fills
   the log table and dashboard charts.

## Notes on going further
- This uses SQLite (`instance/safety.db`) — fine for a pilot; swap
  `SQLALCHENY_DATABASE_URI` for Postgres/MySQL for production.
- The dashboard no longer records audio itself — the recorder app posts audio to
  `/api/webhook/voice-observation` (see above). Once you deploy this backend live (not just
  `localhost`), give the recorder app the deployed URL + `WEBHOOK_API_KEY`.
- All charts are Chart.js, all data comes live from `/api/observations` — nothing is hardcoded.
- To reset and reseed sample data matching your example log, you can POST to
  `/admin/observations` (as admin, logged in) with each row's data, or add a small
  seed script — happy to add one if useful.
