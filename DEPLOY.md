# Deployment Guide for Network Intrusion Detection System

## 0. Prerequisite: Fork the Repository
**Since the code is on your friend's GitHub**, you must **Fork** it to your own account to see it in Render/Netlify.
1.  Go to your friend's repository page on GitHub.
2.  Click the **Fork** button (top right corner).
3.  Select your own account.
4.  Now you have a copy under `your-username/repository-name`. Use *this* copy for proper deployment.

---

## 1. Backend Deployment (Render)

1.  **Create a New Web Service** on [Render](https://render.com/).
2.  **Connect your repository** (the one you just forked).
3.  **Important**: In the **Branch** dropdown, select `modified` (or whichever branch has the latest code).
4.  **Settings**:
    -   **Root Directory**: `backend/Detect`
    -   **Runtime**: Python 3
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `gunicorn server:app`
5.  **Environment Variables**:
    -   Set `PYTHON_VERSION` to `3.9.0` (or your preferred version).
6.  **Deploy**. Once finished, copy the **Render URL** (e.g., `https://nids-backend.onrender.com`).

> **Note**: The backend will likely *not* be able to sniff packets in the cloud environment due to permissions. It will run in a "passive" mode where it stays alive but might not show live traffic.

---

## 2. Frontend Deployment (Netlify)

1.  **Create a New Site** on [Netlify](https://www.netlify.com/).
2.  **Import from GitHub**.
3.  **Connect your repository** (the one you just forked).
4.  **Important**: In the **Branch to deploy** field, select `modified`.
5.  **Settings**:
    -   **Base Directory**: `frontend/nids-frontend`
    -   **Build Command**: `npm run build`
    -   **Publish Directory**: `frontend/nids-frontend/dist`
6.  **Environment Variables** (Advanced Settings):
    -   Key: `VITE_API_URL`
    -   Value: `https://nids-backend.onrender.com` (The URL you got from Render, **without** a trailing slash).
7.  **Deploy Site**.

## 3. Local Development
To run locally now:
-   **Backend**: `python server.py`
-   **Frontend**: `npm run dev`
    -   Make sure `server.py` is running on port 5000.
    -   The frontend will automatically fallback to `http://127.0.0.1:5000` if `VITE_API_URL` is not set.
