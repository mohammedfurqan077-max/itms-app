# ITMS Frontend Documentation

## Overview

This documentation provides complete guidance for building the frontend of the Intelligent Traffic Management System (ITMS) that integrates perfectly with the existing backend.

---

## Documentation Structure

### 📄 [01-API-ENDPOINTS.md](./01-API-ENDPOINTS.md)
**Complete API Reference**
- All 5 API modules (Auth, System, Control, Junctions, Commands)
- Request/response examples for every endpoint
- Command types and system modes
- Authentication requirements
- Status codes

### 📦 [02-DATA-MODELS.md](./02-DATA-MODELS.md)
**TypeScript Interfaces & Data Models**
- Complete TypeScript interfaces for all backend models
- Enums for all status types
- Request/response types
- Validation rules
- Example usage in React/TypeScript

### 🏗️ [03-FRONTEND-STRUCTURE.md](./03-FRONTEND-STRUCTURE.md)
**Recommended Frontend Architecture**
- Complete project structure
- Tech stack recommendations
- File organization
- API client setup with interceptors
- State management examples
- Routing configuration
- Custom hooks

### 🎨 [04-PAGE-DESIGNS.md](./04-PAGE-DESIGNS.md)
**Page Layouts & UI Designs**
- 6 main pages with visual layouts
- Feature lists for each page
- Component breakdowns
- Responsive design guidelines
- Common UI components

### 🔌 [05-INTEGRATION-GUIDE.md](./05-INTEGRATION-GUIDE.md)
**Backend Integration Guide**
- Authentication flow
- Data fetching patterns
- Form handling
- Error handling
- WebSocket real-time updates
- Performance optimization
- Testing strategies
- Deployment guide

---

## Quick Start

### 1. Read the Documentation in Order

1. **Start with API Endpoints** - Understand what the backend provides
2. **Review Data Models** - Know the data structures
3. **Study Frontend Structure** - Learn the recommended architecture
4. **Check Page Designs** - Visualize the UI
5. **Follow Integration Guide** - Implement the connection

### 2. Setup Development Environment

```bash
# Create React + TypeScript project
npm create vite@latest itms-frontend -- --template react-ts
cd itms-frontend

# Install dependencies
npm install axios react-router-dom @reduxjs/toolkit react-redux
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install recharts date-fns

# Start development
npm run dev
```

### 3. Configure Backend Connection

Create `.env.development`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 4. Test Backend Connection

```typescript
// Test login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@itms.com',
    password: 'admin123'
  })
});

const data = await response.json();
console.log('Login successful:', data);
```

---

## Backend Summary

### Base URL
```
http://localhost:8000/api/v1
```

### Available Modules

1. **Authentication** (`/auth`)
   - Login, Register, Logout
   - Token refresh
   - Password management

2. **System State** (`/system`)
   - Get/update system mode
   - System state management

3. **Control System** (`/control`)
   - Switch modes
   - Set lane timings
   - VIP override
   - Emergency stop

4. **Junction Management** (`/junctions`)
   - CRUD operations
   - Status management
   - Statistics

5. **Command Execution** (`/commands`)
   - Send commands
   - Track execution
   - Retry/cancel
   - Statistics

### Test Credentials

**Admin:**
- Email: `admin@itms.com`
- Password: `admin123`

**Jawan:**
- Email: `jawan@itms.com`
- Password: `jawan123`

---

## Key Features to Implement

### Must-Have Features

1. **Authentication**
   - ✅ Login/logout
   - ✅ Token management
   - ✅ Protected routes
   - ✅ Role-based access

2. **Dashboard**
   - ✅ System overview
   - ✅ Junction statistics
   - ✅ Recent commands
   - ✅ Quick actions

3. **Junction Management**
   - ✅ List junctions
   - ✅ Create/edit/delete
   - ✅ Status monitoring
   - ✅ Search and filter

4. **Traffic Control**
   - ✅ Mode switching
   - ✅ Lane timing control
   - ✅ VIP mode
   - ✅ Emergency stop

5. **Command History**
   - ✅ View commands
   - ✅ Filter by status/type
   - ✅ Retry failed commands
   - ✅ Statistics

### Nice-to-Have Features

- 🔄 Real-time updates (WebSocket)
- 📊 Advanced analytics
- 🗺️ Junction map view
- 📱 Mobile responsive design
- 🔔 Notifications
- 📈 Charts and graphs
- 🌙 Dark mode
- 🌐 Multi-language support

---

## Recommended Tech Stack

### Core
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **State Management**: Redux Toolkit or Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios

### UI/Styling
- **UI Library**: Material-UI (MUI) or Ant Design
- **Icons**: Material Icons
- **Charts**: Recharts
- **Date**: date-fns

### Development
- **Linting**: ESLint + Prettier
- **Testing**: Jest + React Testing Library

---

## Project Timeline Estimate

### Phase 1: Setup & Authentication (1 week)
- Project setup
- API client configuration
- Authentication pages
- Protected routes

### Phase 2: Core Pages (2 weeks)
- Dashboard
- Junction management
- Control panel

### Phase 3: Advanced Features (1 week)
- Command history
- Statistics
- Settings

### Phase 4: Polish & Testing (1 week)
- Error handling
- Loading states
- Responsive design
- Testing

**Total: 5 weeks**

---

## Development Workflow

### 1. Start Backend
```bash
cd backend
docker-compose up -d
# or
uvicorn app.main:app --reload
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Integration
- Login with test credentials
- Test each API endpoint
- Verify data flow

### 4. Build for Production
```bash
npm run build
```

---

## Common Issues & Solutions

### CORS Errors
**Problem**: Browser blocks API requests

**Solution**: Backend already has CORS configured. Ensure frontend URL is in `ALLOWED_ORIGINS` in backend `.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 401 Unauthorized
**Problem**: Token expired or invalid

**Solution**: Implement token refresh in axios interceptor (see Integration Guide)

### Network Errors
**Problem**: Cannot connect to backend

**Solution**: 
- Check backend is running: `http://localhost:8000/health`
- Verify API base URL in frontend `.env`

---

## Support & Resources

### Backend Documentation
- `backend/README.md` - Backend overview
- `backend/ARCHITECTURE.md` - Architecture details
- `backend/API_QUICK_REFERENCE.md` - Quick API reference
- Swagger UI: `http://localhost:8000/api/docs`

### Frontend Documentation
- This folder contains all frontend documentation
- Each file is self-contained and detailed

### Testing
- Use Postman or curl to test APIs
- Backend includes test scripts
- Example requests in API documentation

---

## Next Steps

1. **Read all documentation files** in order
2. **Setup development environment**
3. **Test backend APIs** with Postman/curl
4. **Start with authentication** implementation
5. **Build pages incrementally**
6. **Test integration** at each step
7. **Add polish and error handling**
8. **Deploy to production**

---

## Contact

For questions about the backend or API:
- Check backend documentation
- Review API examples
- Test with Swagger UI

For frontend implementation:
- Follow this documentation
- Refer to code examples
- Use recommended patterns

---

**Good luck building the ITMS frontend!** 🚀

This documentation provides everything needed to create a production-ready frontend that perfectly integrates with the ITMS backend.
