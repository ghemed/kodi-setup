# 📺 Kodi SharePoint Video Addon

Stream videos from a private SharePoint / OneDrive for Business share directly in Kodi — no Microsoft account required on the viewer's side. Built for sharing a personal video library with friends and family across Android TV, Android phones, and Windows.

---

## How It Works

The addon authenticates silently using Microsoft Graph API with app-only credentials (OAuth2 client credentials flow). Viewers never log in — they just get a SharePoint share link that you generate for them, configure once via this setup page, and then browse and stream directly in Kodi.

```
SharePoint Share URL
        │
        ▼
  GitHub Gist ──► credentials (tenant/client/secret)
        │
        ▼
  Microsoft Graph API ──► resolve share → list files → download URLs
        │
        ▼
     Kodi player
```

Credentials are fetched at runtime from a private GitHub Gist (5-minute cache), so you can rotate them without redistributing the addon.

---

## Features

- 🎬 Browse and stream videos from a SharePoint folder
- 📁 Subfolder navigation
- 📝 Auto-matched subtitles (`.srt`, `.ass`, `.vtt`, etc. matched by filename)
- 📺 PIN-based pairing for Android TV (no keyboard needed)
- 🖥 Auto-configuration for Windows via Kodi JSON-RPC
- 📱 One-tap setup for Android phones via Intent deep link
- 🔍 Built-in diagnostic log viewer inside Kodi
- 🔄 Credential rotation without addon update (via Gist)

---

## Requirements

| Component | Requirement |
|-----------|------------|
| Kodi | v19 (Matrix) or later |
| Python | 3.x (bundled with Kodi 19+) |
| Platform | Android TV, Android, Windows (any Kodi-supported OS) |
| Microsoft | SharePoint / OneDrive for Business tenant |
| Azure AD | App registration with `Files.Read.All` permission |

---

## Repository Structure

```
kodi-setup/
├── README.md
├── index.html                          ← GitHub Pages setup page
└── plugin.video.onedriveshare/
    ├── addon.xml
    ├── addon.py                        ← Main entry point, router, PIN pairing
    └── resources/
        ├── settings.xml
        ├── __init__.py
        └── lib/
            ├── __init__.py
            ├── config.py               ← Fetches credentials from GitHub Gist
            ├── auth.py                 ← OAuth2 client credentials token manager
            └── sharepoint.py          ← Microsoft Graph API file listing
```

---

## Setup

### 1. Azure App Registration

1. Go to [portal.azure.com](https://portal.azure.com) → **Azure Active Directory** → **App registrations** → **New registration**
2. Name it anything (e.g. `KodiVideoAddon`), leave defaults, click **Register**
3. Note your **Tenant ID** and **Application (client) ID**
4. Go to **Certificates & secrets** → **New client secret** → copy the secret **value**
5. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Application permissions** → add `Files.Read.All`
6. Click **Grant admin consent**

### 2. GitHub Gist (Credential Store)

Create a **secret** GitHub Gist with the filename `config.json`:

```json
{
  "tenant_id": "your-tenant-id",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret"
}
```

Copy the **raw URL** of the gist (the URL ending in `/raw/config.json`) and update `GIST_URL` in `resources/lib/config.py`.

> **Security note:** Use a *secret* gist (not public) and keep the raw URL private. Anyone with the URL can read the credentials.

### 3. GitHub Pages

1. Push this repository to GitHub
2. Go to **Settings** → **Pages** → Source: **main branch, root folder**
3. Your setup page will be live at `https://YOUR_USERNAME.github.io/REPO_NAME/`
4. Update `SETUP_URL` in `index.html` to match

### 4. Package the Addon

```bash
zip -r plugin.video.onedriveshare.zip plugin.video.onedriveshare/
```

Commit the zip to the repository root so the setup page can link to it for download.

---

## Installing the Addon

### Android TV (PIN pairing — no keyboard needed)

1. Transfer the `.zip` to the TV (USB drive, or download via the TV's browser)
2. In Kodi: **Add-ons** → 📦 box icon (top left) → **Install from zip** → select the file
3. If Kodi crashes on first install, close and install again — this is a known Kodi/Android quirk, the second install always works
4. Open the addon — it will show a **4-digit PIN** on screen
5. On your phone, go to the setup page, choose **Android TV**, enter the PIN and your SharePoint link
6. The TV receives the URL and loads your videos

### Android Phone

1. Download the `.zip` from the setup page
2. Install via Kodi: **Add-ons** → 📦 → **Install from zip** → **Downloads** → select file
3. Go to the setup page on your phone, choose **Android Phone**, paste your SharePoint link, tap **Open in Kodi**
4. Kodi opens and configures itself via Android Intent

### Windows

1. Download the `.zip` and install via Kodi: **Add-ons** → 📦 → **Install from zip**
2. Enable Kodi's HTTP control: **Settings** → **Services** → **Control** → turn on **Allow remote control via HTTP** (port 8080)
3. Go to the setup page in a browser on the same PC, choose **Windows PC**, paste your link, click **Configure Kodi Automatically**
4. The page installs the addon, saves the URL, and opens the video library — no manual steps

---

## Sharing With Friends

Each friend gets their own SharePoint share link (generated from your SharePoint). Send them their link via WhatsApp, email, etc., along with the setup page URL.

They never need to create accounts or handle credentials — just install the addon once and paste their link.

**To generate a shareable pre-filled setup link:**

Go to the setup page → choose **Just the link** → paste the SharePoint URL → copy the generated link. Share this directly and they only need to choose their device type.

---

## Supported File Types

**Video:** `.mp4` `.mkv` `.avi` `.mov` `.wmv` `.m4v` `.mpg` `.mpeg` `.ts` `.m2ts` `.flv` `.webm`

**Subtitles (auto-matched by filename):** `.srt` `.sub` `.ass` `.ssa` `.vtt`

---

## Diagnostic Log

If something isn't working, the addon writes a detailed log to:

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\Kodi\kodi.log` and `onedriveshare_debug.log` in the same folder |
| Android | `/Android/data/org.xbmc.kodi/files/.kodi/temp/onedriveshare_debug.log` |

You can also read the log directly inside Kodi — open the addon and tap **View debug log** at the bottom of the listing. It shows the last 200 lines in a scrollable dialog, including full tracebacks on errors.

The log records: startup, argument parsing, library imports, credential fetching, token acquisition, Graph API calls, and all errors with tracebacks.

---

## Rotating Credentials

If you need to revoke access or rotate the client secret:

1. Generate a new secret in your Azure App Registration
2. Update your GitHub Gist `config.json` with the new values
3. No addon update or redistribution needed — all devices pick up the new credentials within 5 minutes (cache TTL)

---

## Troubleshooting

**Addon crashes on first install (Android)**
This is a known Kodi/Android issue with first-time plugin registration. Close Kodi completely and install the zip again — the second install always succeeds.

**`module 'xbmc' has no attribute 'translatePath'`**
You have an older version of the addon. Install v1.0.4 or later — this uses `xbmcvfs.translatePath` which is correct for Kodi 19+.

**"Could not fetch credentials"**
Check that your Gist raw URL is correct and accessible. The URL must end in `/raw/config.json` (not the normal gist view URL). Also verify the JSON is valid and contains all three keys.

**"Graph API error (HTTP 401)"**
The access token is invalid or expired. Check that your Azure app has `Files.Read.All` application permission with admin consent granted.

**"Could not resolve share link to a drive item"**
The SharePoint share URL is invalid or has expired. Regenerate the share link from SharePoint and reconfigure via the setup page.

**Windows: setup page can't reach Kodi**
Make sure Kodi is running and HTTP control is enabled: **Settings** → **Services** → **Control** → **Allow remote control via HTTP** (port 8080, no password).

**Android TV: PIN not received by TV**
Both your phone and TV must be on the same WiFi network. Also verify Kodi's HTTP control is enabled on the TV (same setting as Windows above) — this is what allows the phone to push the URL to the TV.

---

## License

GPL-2.0-or-later
