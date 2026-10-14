# Gaia Detector

AI Content Authenticity Detection application combining a modern React + Vite frontend, a FastAPI backend, MongoDB Atlas storage, Google Drive integration, and Hugging Face CLIP inference.

---

## 1. Architecture Overview

```
Frontend (React 19 + Vite + Tailwind CSS)
   │ (credentials: include via httpOnly cookie)
   ▼
FastAPI Backend (Port 8000)
   ├── Auth Guard (JWT httpOnly cookie / Bearer fallback)
   ├── AI Detector (CLIP zero-shot inference for images)
   ├── Google Drive Service (stores uploaded files privately)
   └── MongoDB Atlas (stores users, uploads metadata, detection history)
```

- **Frontend**: React 19, Vite 8, Tailwind CSS, React Router DOM 7, Framer Motion.
- **Backend**: FastAPI, Uvicorn, Pydantic Settings, direct bcrypt hashing, python-jose.
- **Database**: MongoDB Atlas (`motor` async driver) for users, metadata, detection history, and reports.
- **File Storage**: Google Drive API (files remain strictly private; Drive file IDs stored in MongoDB).
- **AI Detection**: Zero-shot image classification replicating `Detector.html` via Hugging Face `transformers` CLIP (`openai/clip-vit-base-patch32`). Text, document, and video endpoints report honest unmounted status without synthetic scores.

---

## 2. Prerequisites

- **Python 3.11+** (Python 3.14 compatible)
- **Node.js 18+** and **npm 9+**
- (Optional) **MongoDB Atlas** cluster URI
- (Optional) **Google Cloud** service account JSON key & Drive destination folder ID

---

## 3. Local Development Setup (Windows PowerShell)

### Step 1: Clone Repository
```powershell
git clone https://github.com/Prithvirajsinh7578/Gaia-Detector.git
cd Gaia-Detector
```

### Step 2: Backend Setup
```powershell
cd backend

# Install Python dependencies
python -m pip install -r requirements.txt

# Create .env from template
Copy-Item .env.example .env

# Run automated tests
python -m pytest tests/test_backend.py -v

# Start FastAPI development server (runs on http://localhost:8000)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup
In a separate PowerShell terminal:
```powershell
cd frontend/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Start Vite development server (runs on http://localhost:5173)
npm run dev
```

The Vite dev server automatically proxies API requests (`/auth`, `/detect`, `/upload`, `/history`, `/report`, `/health`, `/ready`) to `http://localhost:8000`.

---

## 4. Environment Variables Reference

### Backend (`backend/.env`)

| Variable | Description | Default / Example |
|---|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://<user>:<pass>@cluster.mongodb.net/gaiadetector` |
| `MONGODB_DB_NAME` | Database name | `gaiadetector` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRY_MINUTES` | Token expiration duration | `10080` (7 days) |
| `COOKIE_SECURE` | Set to `true` in production with HTTPS | `false` |
| `COOKIE_SAMESITE` | Cookie SameSite policy | `lax` |
| `COOKIE_NAME` | Cookie name for the JWT token | `gaia_access_token` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173,http://localhost:3000` |
| `GOOGLE_SERVICE_ACCOUNT_JSON_PATH` | Path to Google Service Account JSON | `C:/path/to/service-account.json` |
| `GOOGLE_DRIVE_FOLDER_ID` | Drive folder ID for uploads | Google Drive Folder ID |
| `BACKEND_PORT` | FastAPI server port | `8000` |
| `MAX_UPLOAD_SIZE_MB` | Maximum allowed file size | `50` |

### Frontend (`frontend/frontend/.env`)

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Optional API base URL for production builds (empty in dev for proxying) |

---

## 5. API Reference Summary

- `GET /health`: Process liveness check.
- `GET /ready`: Readiness check (verifies database availability).
- `POST /auth/register`: Create user account and set `httpOnly` cookie.
- `POST /auth/login`: Authenticate and set `httpOnly` cookie.
- `POST /auth/logout`: Invalidate session and clear `httpOnly` cookie.
- `GET /auth/me`: Get current authenticated user session.
- `POST /upload` (and `POST /api/upload`): Upload file to Google Drive and store metadata.
- `POST /detect/image`: Run CLIP AI detection on image file.
- `POST /detect/text`: Submit text for authenticity verification.
- `POST /detect/document`: Submit PDF/TXT document for text extraction & analysis.
- `POST /detect/video`: Submit video for authenticity analysis.
- `GET /history`: List user detection history (paginated, user-scoped).
- `GET /history/{id}`: Inspect specific past detection record.
- `GET /report/{id}`: Detailed diagnostic report.

---

## 6. Security Guarantees

1. **No Tokens in LocalStorage**: Authentication tokens are strictly delivered and read via `httpOnly` cookies with `SameSite=lax`.
2. **User Data Isolation**: History and report lookups strictly enforce current authenticated user scoping, preventing ID guessing.
3. **Private File Storage**: Uploaded files to Google Drive are not made public.
4. **No Hardcoded Secrets**: Secrets and credentials are never stored in code; all fallbacks gracefully report unconfigured status.
