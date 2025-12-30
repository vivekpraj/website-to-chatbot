**Website-to-Chatbot SaaS Platform**
**1. Project Overview**

1.1 Problem Statement

Creating a chatbot specific to a business website is traditionally:

Expensive and agency-dependent

Time-consuming to build and maintain

Inaccessible to small businesses and individuals

Locked behind technical AI expertise

Most businesses must contact AI agencies, share internal data manually, and wait weeks before receiving a usable chatbot.

This creates a major adoption barrier despite growing demand for AI-powered customer support.

1.2 Motivation & Gap Identified

I observed that:

Businesses want AI chatbots for FAQs, services, onboarding, and support

Existing solutions are either generic or costly

There is no simple way to convert your own website into a chatbot instantly

Key gap:
👉 Website-specific chatbots are not self-service.

1.3 Solution Overview

This project solves that gap by providing a self-serve SaaS platform where:

Any user can input a website URL

The system automatically trains a chatbot on that website

A shareable chatbot link is generated instantly

No AI knowledge or agencies are required

**2. What the SaaS Does**

2.1 Core Capabilities

Convert any website into an AI chatbot

Crawl multiple pages automatically

Use Retrieval-Augmented Generation (RAG)

Generate a public chat URL per bot

Allow sharing via WhatsApp, Instagram, Telegram, etc.

2.2 End-to-End Workflow
User registers/logs in
        ↓
Creates bot using website URL
        ↓
Website is crawled (multi-page)
        ↓
Text cleaned and chunked
        ↓
Embeddings generated
        ↓
Stored in vector database
        ↓
Bot marked READY
        ↓
Public chat URL generated

2.3 Public Chatbot Usage

Anyone can open the chat URL

Ask questions about the website

AI answers strictly using website content

No authentication required for public chat

**3. System Architecture**
   
3.1 High-Level Architecture
Frontend (Next.js)
        ↓
FastAPI Backend
        ↓
PostgreSQL / SQLite
        ↓
Chroma Vector DB
        ↓
Gemini LLM

3.2 Technology Stack
Backend

Python + FastAPI

SQLAlchemy ORM

JWT Authentication

Role-Based Access Control (RBAC)

ChromaDB (vector store)

Gemini LLM (answer generation)

Frontend

Next.js (App Router)

Tailwind CSS

Fetch API

Client-side JWT handling

Role-aware UI rendering

**4. User Roles & Permissions**

4.1 Client

Clients can:

Register and login

Create chatbots from websites

View only their own bots

Access bot metrics

Share chatbot URLs publicly

4.2 Super Admin

Super Admin can:

View all users

View all bots

Delete users

Monitor platform usage

Access admin-only APIs and UI

RBAC is enforced both in backend APIs and frontend rendering.

**5. AI & RAG Pipeline**

5.1 Website Crawling

Multi-page crawling

URL normalization

Page-wise content extraction

Failure-safe crawling

5.2 Text Cleaning

Navbar/footer noise removal

Duplicate line removal

Email/phone filtering

Short junk line elimination

5.3 Chunking Strategy

Fixed-size semantic chunks

Page-level metadata retention

Optimized for vector retrieval

5.4 Vector Embeddings

Each chunk converted to embeddings

Stored in ChromaDB

Linked to bot ID and page URL

5.5 Answer Generation (RAG)

User question embedded

Relevant chunks retrieved

Context injected into LLM prompt

Gemini generates grounded response

The model never answers outside retrieved context.

**6. Backend Structure**

app/
├── main.py

├── db.py

├── models.py

├── schemas.py

├── routers/

│   ├── auth.py

│   ├── bots.py

│   ├── chat.py

│   └── admin.py

├── services/

│   ├── crawler.py

│   ├── cleaner.py

│   ├── text_processing.py

│   ├── embeddings.py

│   ├── vector_store.py

│   └── gemini_client.py


Each layer is cleanly separated:

Routers → API layer

Services → business logic

Models → database schema

**7. Frontend Structure**
app/
├── login/
│   └── page.tsx
├── register/
│   └── page.tsx
├── dashboard/
│   └── page.tsx
├── chat/
│   └── [botId]/
│       └── page.tsx
├── admin/
│   ├── users/
│   │   └── page.tsx
│   └── bots/
│       └── page.tsx
lib/
├── auth.ts
├── constants.ts

**8. Authentication & Authorization**

8.1 JWT Authentication

Token generated on login

Stored in localStorage

Sent via Authorization: Bearer <token>

8.2 Frontend Role Awareness

JWT decoded on client

Role extracted (client / super_admin)

UI rendered conditionally based on role

**9. Metrics & Monitoring**

Tracked per bot:

Message count

Last used timestamp

Creation date

Bot status

Exposed via secured APIs and shown in dashboard.

**10. Shareable Chat URLs**

Each bot generates a public link:

/chat/{bot_id}


Clients can share this link on:

WhatsApp

Instagram bio

Telegram groups

Customer support chats

**11. Future Enhancements**

Iframe-based chatbot embedding

Advanced analytics dashboard

Custom UI themes per client

Subscription plans & rate limits

Multiple LLM provider support

**12. Local Setup**

Backend

pip install -r requirements.txt

uvicorn app.main:app --reload

Frontend

npm install

npm run dev

**13. Why This Project Matters**

This project demonstrates:

Real-world application of LLMs and RAG

SaaS-grade backend architecture

Secure multi-user system design

Thoughtful frontend role-based UX

Ownership-driven AI product thinking

It removes a major barrier in AI adoption by making website-specific chatbots accessible to everyone.
