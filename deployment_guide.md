# SmartAttend-IoT Deployment Guide

This guide details how to deploy the **Frontend to Netlify** and the **Backend to Vercel**.

> [!WARNING] > **Critical Backend Requirement**: Vercel is a serverless platform and **does not support persistent SQLite files** (`backend.db`). Every time the server sleeps (inactivity), the database will be reset.
> **Solution**: You MUST use a hosted PostgreSQL database (e.g., [Supabase](https://supabase.com/), [Neon](https://neon.tech/), or [Render Postgres](https://render.com/)). This guide assumes **Supabase**.

---

## 1. Backend Deployment (Vercel)

### Prerequisites

1.  **Vercel Account**: [Sign up here](https://vercel.com/signup).
2.  **Supabase Account**: [Create a project here](https://supabase.com/).
3.  **Vercel CLI** (Optional but recommended): `npm i -g vercel`

### Step 1: Configure Database (Supabase)

1.  Create a new project on Supabase.
2.  Go to **Project Settings -> Database**.
3.  Copy the **Connection String (URI)**. It looks like:
    `postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`
4.  Replace `[PASSWORD]` with your actual DB password.
5.  **Important**: Keep this URL safe.

### Step 2: Prepare Backend Code

1.  Create a `vercel.json` file in the `backend/` directory:
    ```json
    {
      "builds": [
        {
          "src": "main.py",
          "use": "@vercel/python"
        }
      ],
      "routes": [
        {
          "src": "/(.*)",
          "dest": "main.py"
        }
      ]
    }
    ```
2.  Ensure `backend/requirements.txt` includes:
    - `fastapi`
    - `uvicorn[standard]`
    - `sqlalchemy`
    - `asyncpg` (Required for Postgres)
    - `psycopg2-binary`
    - `python-multipart`
    - `python-dotenv`
    - `alembic` (Optional, for migrations)

### Step 3: Deploy to Vercel

1.  Go to your Vercel Dashboard -> **New Project**.
2.  Import your GitHub repository.
3.  **Root Directory**: Set this to `backend`.
4.  **Environment Variables**: Add the following:
    - `DATABASE_URL`: Paste your Supabase Connection String.
    - `PYTHON_VERSION`: `3.9` (Recommended compatibility).
5.  Click **Deploy**.

---

## 2. Frontend Deployment (Netlify)

### Prerequisites

1.  **Netlify Account**: [Sign up here](https://www.netlify.com/).

### Step 1: Configure Nuxt for Production

1.  Ensure `frontend/nuxt.config.ts` targets the production backend URL.
    - You can use `.env` variables in Nuxt.
    - Example: `const backendUrl = process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'`
2.  Update your `frontend/app/composables/useApi.ts` (or similar) to use this base URL.

### Step 2: Deploy to Netlify

1.  Log in to Netlify.
2.  Click **Add new site** -> **Import an existing project**.
3.  Select generic **GitHub** and pick your repo.
4.  **Build Settings**:
    - **Base directory**: `frontend`
    - **Build command**: `npm run generate` (Static) or `npm run build` (Server side)
    - **Publish directory**: `dist` or `.output/public`
5.  **Environment Variables**:
    - `NUXT_PUBLIC_API_BASE`: Set this to your **Vercel Backend URL** (e.g., `https://smartattend-backend.vercel.app`).
6.  Click **Deploy Site**.

---

## 3. Post-Deployment Setup

1.  **Frontend**: Visit your Netlify URL. It should load the Dashboard.
2.  **Students**: Register a new student to test the Database connection.
3.  **IoT Client**:
    - Update your Raspberry Pi / Local Python script to point to the new **Vercel Backend URL**.
    - Run `main.py` locally.
    - Ideally, the IoT client should remain running on the Edge (Raspberry Pi), connecting to your Vercel/Netlify cloud.
