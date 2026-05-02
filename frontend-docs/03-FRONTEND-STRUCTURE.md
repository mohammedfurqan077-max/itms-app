# ITMS Frontend - Recommended Structure

## Recommended Tech Stack

### Core
- **Framework**: React 18+ with TypeScript
- **State Management**: Redux Toolkit or Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **WebSocket**: Socket.IO Client (for real-time updates)

### UI/Styling
- **UI Library**: Material-UI (MUI) or Ant Design
- **Icons**: Material Icons or React Icons
- **Charts**: Recharts or Chart.js
- **Maps**: Leaflet or Google Maps (for junction locations)

### Development
- **Build Tool**: Vite or Create React App
- **Linting**: ESLint + Prettier
- **Testing**: Jest + React Testing Library

---

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
│
├── src/
│   ├── api/                    # API client and endpoints
│   │   ├── client.ts           # Axios instance with interceptors
│   │   ├── auth.api.ts         # Authentication APIs
│   │   ├── system.api.ts       # System state APIs
│   │   ├── control.api.ts      # Control system APIs
│   │   ├── junctions.api.ts    # Junction management APIs
│   │   ├── commands.api.ts     # Command execution APIs
│   │   └── index.ts            # Export all APIs
│   │
│   ├── components/             # Reusable components
│   │   ├── common/             # Common UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Loader.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   │
│   │   ├── layout/             # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── MainLayout.tsx
│   │   │
│   │   ├── auth/               # Auth-related components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── RoleGuard.tsx
│   │   │
│   │   ├── junction/           # Junction components
│   │   │   ├── JunctionCard.tsx
│   │   │   ├── JunctionList.tsx
│   │   │   ├── JunctionForm.tsx
│   │   │   ├── JunctionStatus.tsx
│   │   │   └── JunctionMap.tsx
│   │   │
│   │   ├── control/            # Control panel components
│   │   │   ├── ControlPanel.tsx
│   │   │   ├── LaneControl.tsx
│   │   │   ├── ModeSelector.tsx
│   │   │   ├── TimingControl.tsx
│   │   │   └── VIPControl.tsx
│   │   │
│   │   ├── command/            # Command components
│   │   │   ├── CommandList.tsx
│   │   │   ├── CommandCard.tsx
│   │   │   ├── CommandForm.tsx
│   │   │   └── CommandStats.tsx
│   │   │
│   │   └── dashboard/          # Dashboard components
│   │       ├── StatCard.tsx
│   │       ├── Chart.tsx
│   │       ├── RecentActivity.tsx
│   │       └── SystemStatus.tsx
│   │
│   ├── pages/                  # Page components
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   └── DashboardPage.tsx
│   │   │
│   │   ├── junctions/
│   │   │   ├── JunctionsPage.tsx
│   │   │   ├── JunctionDetailPage.tsx
│   │   │   └── CreateJunctionPage.tsx
│   │   │
│   │   ├── control/
│   │   │   └── ControlPage.tsx
│   │   │
│   │   ├── commands/
│   │   │   ├── CommandsPage.tsx
│   │   │   └── CommandDetailPage.tsx
│   │   │
│   │   ├── settings/
│   │   │   ├── ProfilePage.tsx
│   │   │   └── SettingsPage.tsx
│   │   │
│   │   └── NotFoundPage.tsx
│   │
│   ├── store/                  # State management
│   │   ├── index.ts            # Store configuration
│   │   ├── slices/             # Redux slices or Zustand stores
│   │   │   ├── authSlice.ts
│   │   │   ├── systemSlice.ts
│   │   │   ├── junctionSlice.ts
│   │   │   ├── commandSlice.ts
│   │   │   └── uiSlice.ts
│   │   └── hooks.ts            # Custom hooks for store
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useJunctions.ts
│   │   ├── useCommands.ts
│   │   ├── useWebSocket.ts
│   │   └── useDebounce.ts
│   │
│   ├── types/                  # TypeScript types
│   │   ├── user.types.ts
│   │   ├── junction.types.ts
│   │   ├── command.types.ts
│   │   ├── control.types.ts
│   │   └── index.ts
│   │
│   ├── utils/                  # Utility functions
│   │   ├── auth.utils.ts       # Token management
│   │   ├── date.utils.ts       # Date formatting
│   │   ├── validation.utils.ts # Form validation
│   │   └── constants.ts        # App constants
│   │
│   ├── routes/                 # Route configuration
│   │   ├── index.tsx           # Main router
│   │   ├── PrivateRoutes.tsx   # Protected routes
│   │   └── PublicRoutes.tsx    # Public routes
│   │
│   ├── styles/                 # Global styles
│   │   ├── globals.css
│   │   ├── variables.css
│   │   └── theme.ts            # MUI theme or styled-components theme
│   │
│   ├── config/                 # Configuration
│   │   ├── api.config.ts       # API configuration
│   │   └── app.config.ts       # App configuration
│   │
│   ├── App.tsx                 # Root component
│   ├── main.tsx                # Entry point
│   └── vite-env.d.ts           # Vite types
│
├── .env.example                # Environment variables template
├── .env.development            # Development environment
├── .env.production             # Production environment
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## Key Files Implementation

### 1. API Client (`src/api/client.ts`)

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data.tokens;
        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

### 2. Auth API (`src/api/auth.api.ts`)

```typescript
import { apiClient } from './client';
import { LoginRequest, LoginResponse, User, RegisterRequest } from '../types';

export const authAPI = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  refreshToken: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  changePassword: async (data: { current_password: string; new_password: string }): Promise<void> => {
    await apiClient.post('/auth/change-password', data);
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post(`/auth/logout?refresh_token=${refreshToken}`);
  },
};
```

### 3. Protected Route Component

```typescript
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};
```

### 4. Main Router (`src/routes/index.tsx`)

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import { MainLayout } from '../components/layout/MainLayout';

// Pages
import LoginPage from '../pages/auth/LoginPage';
import DashboardPage from '../pages/dashboard/DashboardPage';
import JunctionsPage from '../pages/junctions/JunctionsPage';
import ControlPage from '../pages/control/ControlPage';
import CommandsPage from '../pages/commands/CommandsPage';
import NotFoundPage from '../pages/NotFoundPage';

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/junctions" element={<JunctionsPage />} />
            <Route path="/control" element={<ControlPage />} />
            <Route path="/commands" element={<CommandsPage />} />
          </Route>
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
};
```

### 5. Auth Hook (`src/hooks/useAuth.ts`)

```typescript
import { useEffect, useState } from 'use';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api/auth.api';
import { User } from '../types';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authAPI.login({ email, password });
    localStorage.setItem('access_token', response.tokens.access_token);
    localStorage.setItem('refresh_token', response.tokens.refresh_token);
    setUser(response.user);
    navigate('/dashboard');
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await authAPI.logout(refreshToken);
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    navigate('/login');
  };

  return {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
  };
};
```

---

## Environment Variables

### `.env.example`
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=ITMS
```

### `.env.development`
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=ITMS Dev
```

### `.env.production`
```env
VITE_API_BASE_URL=https://api.itms.com/api/v1
VITE_WS_URL=wss://api.itms.com/ws
VITE_APP_NAME=ITMS
```

---

## State Management Example (Redux Toolkit)

### Auth Slice
```typescript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authAPI } from '../../api/auth.api';
import { User } from '../../types';

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  loading: false,
  error: null,
};

export const loginAsync = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }) => {
    const response = await authAPI.login({ email, password });
    localStorage.setItem('access_token', response.tokens.access_token);
    localStorage.setItem('refresh_token', response.tokens.refresh_token);
    return response.user;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginAsync.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Login failed';
      });
  },
});

export const { logout } = authSlice.actions;
export default authSlice.reducer;
```

---

This structure provides a solid foundation for building the ITMS frontend that perfectly aligns with your backend architecture!
