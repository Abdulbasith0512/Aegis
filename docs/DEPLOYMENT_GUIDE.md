# AegisAI OS Cloud Deployment Guide

This guide outlines the step-by-step instructions to deploy the AegisAI OS platform publicly using free-tier cloud services (Render, Vercel, Neon, Upstash, Neo4j Aura, and Qdrant Cloud).

---

## Phase 1: Managed Cloud Databases Setup

Sign up for the following free services and gather their connection strings.

### 1. PostgreSQL (Neon.tech)
1. Sign up at [Neon.tech](https://neon.tech/).
2. Create a new project named `aegisai`.
3. In the connection details panel, select **Postgres Dialect** `SQLAlchemy` or copy the raw connection string:
   - Format: `postgresql://[USER]:[PASSWORD]@[HOST]/neondb?sslmode=require`
   - *Note*: Replace `postgresql://` with `postgresql+asyncpg://` when setting the environment variable in python.

### 2. Redis (Upstash)
1. Sign up at [Upstash.com](https://upstash.com/).
2. Create a new Serverless Redis database named `aegisai-redis`.
3. Copy the **Redis URL** under the connection details section:
   - Format: `redis://default:[PASSWORD]@[HOST]:[PORT]`

### 3. Neo4j (Neo4j AuraDB)
1. Sign up at [Neo4j Aura](https://neo4j.com/cloud/platform/aura-graph-database/).
2. Create a new free database instance.
3. Download the generated `.txt` file containing your credentials.
4. Copy the **Connection URL** (Bolt protocol):
   - Format: `bolt://[HOST]:7687`

### 4. Qdrant (Qdrant Cloud)
1. Sign up at [Qdrant.tech Cloud Console](https://qdrant.tech/cloud/).
2. Create a new free tier Cluster.
3. Generate an API Key under the Cluster details.
4. Copy your **HTTP Endpoint URL**:
   - Format: `https://[CLUSTER-ID].aws.qdrant.io`

---

## Phase 2: Database Migration & Seeding (Run from Local Machine)

To populate your cloud PostgreSQL database, run the setup steps from your local machine pointing to Neon:

1. Open your local `.env` file in the project root.
2. Temporarily replace the `DATABASE_URL` with your Neon database URL (remember to include the `+asyncpg` driver):
   ```ini
   DATABASE_URL=postgresql+asyncpg://[USER]:[PASSWORD]@[HOST]/neondb?sslmode=require
   ```
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Run the simulator to seed 1M+ rows of initial data directly to the cloud database:
   ```bash
   python scripts/banking_simulator.py
   ```
5. Restore your local `.env` file back to `localhost` parameters for local development.

---

## Phase 3: Deploy FastAPI Backend on Render

1. Sign up at [Render.com](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Link your GitHub repository (`Aegis`).
4. Apply the following settings:
   - **Name**: `aegis-backend`
   - **Language**: `Docker`
   - **Docker Context**: `.`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Instance Type**: `Web Service` (Free Tier is fine, or Starter for faster load times)
5. Click **Advanced** and add these **Environment Variables**:
   - `DATABASE_URL` = `postgresql+asyncpg://[USER]:[PASSWORD]@[HOST]/neondb?sslmode=require`
   - `REDIS_URL` = `redis://default:[PASSWORD]@[HOST]:[PORT]`
   - `NEO4J_URI` = `bolt://[HOST]:7687`
   - `NEO4J_USER` = `neo4j`
   - `NEO4J_PASSWORD` = `[YOUR-AURA-PASSWORD]`
   - `QDRANT_URL` = `https://[CLUSTER-ID].aws.qdrant.io` *(Include Qdrant API Key in headers if generated)*
   - `ENVIRONMENT` = `production`
   - `SECRET_KEY` = `b91656ea9c21ef884218ec7e7a85de92a2aef1e1498bdecc01d1d41396d65a7f`
6. Click **Deploy Web Service**.
   - Render will build the container and provide you with a public URL (e.g. `https://aegis-backend.onrender.com`).

---

## Phase 4: Deploy Next.js Frontend on Vercel

1. Sign up at [Vercel.com](https://vercel.com/).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. Apply the following configurations:
   - **Root Directory**: Select `frontend`
   - **Framework Preset**: `Next.js`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Expand the **Environment Variables** section and add:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://aegis-backend.onrender.com` *(Your live Render backend URL)*
6. Click **Deploy**.

Vercel will compile the Next.js app and give you your production public URL (e.g., `https://aegis-frontend.vercel.app`).
