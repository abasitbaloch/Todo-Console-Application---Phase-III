---
description: Run the Phase 3 AI Chatbot Project
---

This workflow guides you through setting up and running the Phase 3 AI Chatbot version of the Todo Application.

## Prerequisites

1.  **Python 3.11+** installed.
2.  **Node.js 18+** installed.
3.  **PostgreSQL Database** (e.g., local or Neon).
4.  **OpenAI API Key**.

## Step 1: Backend Setup

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  Install dependencies:
    ```bash
    pip install -e .
    ```

3.  Set up environment variables:
    *   Copy `.env.example` to `.env` if it doesn't exist.
    *   Ensure the following are set in `.env`:
        ```env
        DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
        JWT_SECRET=your-secret
        OPENAI_API_KEY=sk-...
        ```

4.  Run migrations:
    ```bash
    python -m alembic upgrade head
    ```

5.  Start the backend server:
    ```bash
    uvicorn src.main:app --reload --port 8000
    ```

## Step 2: Frontend Setup

1.  Open a new terminal and navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  Install dependencies:
    ```bash
    npm install
    ```

3.  Set up environment variables:
    *   Copy `.env.local.example` to `.env.local` if it doesn't exist.
    *   Ensure `AUTH_SECRET` matches the backend `JWT_SECRET`.

4.  Start the frontend server:
    ```bash
    npm run dev
    ```

## Step 3: Access the Application

1.  Open your browser to [http://localhost:3000](http://localhost:3000).
2.  Log in or Register.
3.  Navigate to the Chat interface (usually via a "Chat" link or `/chat`).
