# SmartAttend-IoT Deployment Guide

This guide details how to deploy the **Frontend to Netlify** and the **Backend to Vercel**.

> [!WARNING] > **Critical Backend Requirement**: Vercel is a serverless platform and **does not support persistent SQLite files** (`backend.db`). Every time the server sleeps (inactivity), the database will be reset.
> **Solution**: You MUST use a hosted PostgreSQL database (e.g., [Supabase](https://supabase.com/), [Neon](https://neon.tech/), or [Render Postgres](https://render.com/)). This guide assumes **Supabase**.

---

## 1. Backend Deployment (Render)

> **Why Render?**
> The backend requires `dlib` (Face Recognition), which needs special system libraries like `cmake`. Vercel's standard environment fails to build this. Render fully supports Docker, which solves this problem easily.

### Prerequisites

1.  **Render Account**: [Sign up here](https://render.com/).
2.  **Supabase Account**: For the database.

### Step 1: Configure Database (Supabase)

_Follow the same step as before to get your Connection String._

### Step 2: Deploy to Render

1.  Push your code to **GitHub**.
2.  Log in to **Render Dashboard**.
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.
5.  **Settings**:
    - **Root Directory**: `backend`
    - **Runtime**: `Docker` (Render should detect the `Dockerfile` automatically).
    - **Region**: Choose closest to you.
    - **Instance Type**: Free (or Starter for better performance).
6.  **Environment Variables**:
    - Key: `DATABASE_URL`
    - Value: Your Supabase Connection String.
7.  Click **Create Web Service**.

Render will now build your Docker container (installing `cmake`, compiling `dlib`) and deploy it. This may take 5-10 minutes for the first build.

8.  **Copy the Service URL** (e.g., `https://smartattend-api.onrender.com`). You will need this for the Frontend.

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
