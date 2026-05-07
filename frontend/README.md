# ITMS Admin Panel

Next.js frontend for the ITMS admin/user dashboard.

## Local Development

```bash
npm install
npm run dev
```

Create `.env.local` from `.env.example` and point it at your backend:

```bash
NEXT_PUBLIC_API_BASE_URL=/api
API_SERVER_URL=http://localhost:8000/api
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
```

## Production Hosting

Set these environment variables on the hosting platform:

```bash
NEXT_PUBLIC_API_BASE_URL=/api
API_SERVER_URL=https://your-backend.example.com/api
NEXT_PUBLIC_SOCKET_URL=https://your-backend.example.com
```

Build and run:

```bash
npm run build
npm run start
```

For Vercel or similar Next.js hosts, use:

- Build command: `npm run build`
- Install command: `npm install`
- Output directory: leave empty/default

The frontend includes a Next.js API proxy at `/api/[...path]`, so `API_SERVER_URL` must point to the deployed backend API.
