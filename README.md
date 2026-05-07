# ITMS - Intelligent Traffic Management System

Production web platform for centralized traffic signal monitoring and control.

## Current Direction

This project is now web-only:

- Backend API: `backend/` using FastAPI
- Web app: `frontend/` using Next.js
- Database: PostgreSQL
- Realtime updates: Socket.IO/WebSockets
- Hardware integration: junction controllers through backend services

No Flutter, native mobile, APK, Android, or iOS app is part of the current hosting plan. Mobile users should access the hosted web app in a browser.

## Repository Structure

```text
ITMS_APP/
  backend/       FastAPI backend and database migrations
  frontend/      Next.js web app for admins and field users
  frontend-docs/ Frontend reference material
```

## Frontend Hosting

```bash
cd frontend
npm install
npm run build
npm run start
```

Required frontend hosting environment variables:

```bash
NEXT_PUBLIC_API_BASE_URL=/api
API_SERVER_URL=https://your-backend-url/api
NEXT_PUBLIC_SOCKET_URL=https://your-backend-url
```

For Vercel or another managed Next.js host:

- Install command: `npm install`
- Build command: `npm run build`
- Output directory: default/empty
- Node version: `20.9.0` or newer

## Backend Hosting

Deploy the backend separately and use its public URL in the frontend variables above. The frontend includes a Next.js API proxy at `/api/[...path]`, so browser API calls stay on the same frontend domain while server-side proxy requests go to `API_SERVER_URL`.

## Verification

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

Backend checks depend on the selected hosting provider and database connection. At minimum, confirm:

- Database migrations apply successfully
- Backend health/API docs are reachable
- CORS allows the frontend domain
- Socket.IO endpoint is reachable from the browser

## Deployment Notes

- Do not commit `.env.local`, `.next`, or `node_modules`.
- Keep production secrets in the hosting provider environment settings.
- Use HTTPS for both frontend and backend.
- After deployment, test login, dashboard data, junction control, live map, and realtime socket updates from the hosted URL.
