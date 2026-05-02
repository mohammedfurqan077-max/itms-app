# ITMS Frontend - Backend Integration Guide

## Quick Start Integration

### Step 1: Setup Project

```bash
# Create React + TypeScript project with Vite
npm create vite@latest itms-frontend -- --template react-ts
cd itms-frontend

# Install dependencies
npm install axios react-router-dom @reduxjs/toolkit react-redux
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install recharts date-fns

# Install dev dependencies
npm install -D @types/node
```

### Step 2: Configure Environment

Create `.env.development`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Step 3: Setup API Client

Create `src/api/client.ts` (see 03-FRONTEND-STRUCTURE.md)

---

## Authentication Flow

### 1. Login Process

```typescript
// User enters credentials
const credentials = {
  email: 'admin@itms.com',
  password: 'admin123'
};

// Call login API
const response = await authAPI.login(credentials);

// Store tokens
localStorage.setItem('access_token', response.tokens.access_token);
localStorage.setItem('refresh_token', response.tokens.refresh_token);

// Store user in state
dispatch(setUser(response.user));

// Redirect to dashboard
navigate('/dashboard');
```

### 2. Token Refresh

```typescript
// Automatic token refresh in axios interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      const response = await axios.post('/auth/refresh', {
        refresh_token: refreshToken
      });
      
      localStorage.setItem('access_token', response.data.tokens.access_token);
      
      // Retry original request
      error.config.headers.Authorization = `Bearer ${response.data.tokens.access_token}`;
      return apiClient(error.config);
    }
    return Promise.reject(error);
  }
);
```

### 3. Logout Process

```typescript
const logout = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  // Call logout API
  await authAPI.logout(refreshToken);
  
  // Clear local storage
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  // Clear state
  dispatch(clearUser());
  
  // Redirect to login
  navigate('/login');
};
```

---

## Data Fetching Patterns

### 1. Fetch on Mount

```typescript
const JunctionsPage = () => {
  const [junctions, setJunctions] = useState<Junction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJunctions = async () => {
      try {
        setLoading(true);
        const response = await junctionsAPI.getJunctions();
        setJunctions(response.junctions);
      } catch (error) {
        console.error('Failed to fetch junctions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJunctions();
  }, []);

  if (loading) return <Loader />;

  return <JunctionList junctions={junctions} />;
};
```

### 2. Fetch with Filters

```typescript
const CommandsPage = () => {
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 10,
    status: undefined,
    junction_id: undefined
  });

  const { data, loading } = useCommands(filters);

  const handleFilterChange = (newFilters) => {
    setFilters({ ...filters, ...newFilters });
  };

  return (
    <div>
      <CommandFilters onChange={handleFilterChange} />
      <CommandList commands={data?.commands} loading={loading} />
      <Pagination 
        page={filters.page}
        totalPages={data?.total_pages}
        onChange={(page) => setFilters({ ...filters, page })}
      />
    </div>
  );
};
```

### 3. Fetch with Polling (Auto-refresh)

```typescript
const DashboardPage = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      const data = await junctionsAPI.getStats();
      setStats(data);
    };

    // Initial fetch
    fetchStats();

    // Poll every 30 seconds
    const interval = setInterval(fetchStats, 30000);

    return () => clearInterval(interval);
  }, []);

  return <DashboardStats stats={stats} />;
};
```

---

## Form Handling

### 1. Create Junction Form

```typescript
const CreateJunctionForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    ip_address: '',
    device_id: '',
    zone: '',
    description: ''
  });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validate = () => {
    const newErrors = {};
    
    if (!formData.name) newErrors.name = 'Name is required';
    if (!formData.ip_address) newErrors.ip_address = 'IP address is required';
    
    // Validate IP address format
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (formData.ip_address && !ipRegex.test(formData.ip_address)) {
      newErrors.ip_address = 'Invalid IP address format';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    try {
      setSubmitting(true);
      await junctionsAPI.createJunction(formData);
      
      // Show success message
      toast.success('Junction created successfully');
      
      // Redirect to junctions page
      navigate('/junctions');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create junction');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        name="name"
        label="Name"
        value={formData.name}
        onChange={handleChange}
        error={!!errors.name}
        helperText={errors.name}
        required
      />
      
      <TextField
        name="ip_address"
        label="IP Address"
        value={formData.ip_address}
        onChange={handleChange}
        error={!!errors.ip_address}
        helperText={errors.ip_address}
        required
      />
      
      {/* Other fields... */}
      
      <Button 
        type="submit" 
        disabled={submitting}
      >
        {submitting ? 'Creating...' : 'Create Junction'}
      </Button>
    </form>
  );
};
```

### 2. Control Panel Form

```typescript
const ControlPanel = () => {
  const [mode, setMode] = useState('manual');
  const [timings, setTimings] = useState({
    lane1: 30,
    lane2: 30,
    lane3: 30,
    lane4: 30
  });

  const handleModeChange = async (newMode) => {
    try {
      await controlAPI.switchMode({ mode: newMode });
      setMode(newMode);
      toast.success(`Mode switched to ${newMode}`);
    } catch (error) {
      toast.error('Failed to switch mode');
    }
  };

  const handleTimingChange = (lane, value) => {
    setTimings({
      ...timings,
      [lane]: value
    });
  };

  const handleApplyTimings = async () => {
    try {
      await controlAPI.setManualTimes(timings);
      toast.success('Timings updated successfully');
    } catch (error) {
      toast.error('Failed to update timings');
    }
  };

  return (
    <div>
      <ModeSelector value={mode} onChange={handleModeChange} />
      
      {mode === 'manual' && (
        <div>
          <LaneTimingControl
            lane="lane1"
            value={timings.lane1}
            onChange={(value) => handleTimingChange('lane1', value)}
          />
          {/* Other lanes... */}
          
          <Button onClick={handleApplyTimings}>
            Apply Changes
          </Button>
        </div>
      )}
    </div>
  );
};
```

---

## Error Handling

### 1. Global Error Handler

```typescript
// In axios interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          toast.error(data.error || 'Bad request');
          break;
        case 401:
          // Handle in token refresh interceptor
          break;
        case 403:
          toast.error('You do not have permission to perform this action');
          break;
        case 404:
          toast.error('Resource not found');
          break;
        case 422:
          // Validation errors
          if (data.details) {
            data.details.forEach(err => {
              toast.error(`${err.loc.join('.')}: ${err.msg}`);
            });
          }
          break;
        case 500:
          toast.error('Server error. Please try again later.');
          break;
        default:
          toast.error('An error occurred');
      }
    } else if (error.request) {
      // Request made but no response
      toast.error('Network error. Please check your connection.');
    } else {
      // Something else happened
      toast.error('An unexpected error occurred');
    }
    
    return Promise.reject(error);
  }
);
```

### 2. Component-Level Error Handling

```typescript
const JunctionDetailPage = () => {
  const { id } = useParams();
  const [junction, setJunction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJunction = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await junctionsAPI.getJunction(id);
        setJunction(data);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load junction');
      } finally {
        setLoading(false);
      }
    };

    fetchJunction();
  }, [id]);

  if (loading) return <Loader />;
  if (error) return <ErrorMessage message={error} onRetry={fetchJunction} />;
  if (!junction) return <NotFound />;

  return <JunctionDetail junction={junction} />;
};
```

---

## Real-time Updates (WebSocket)

### 1. WebSocket Setup

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

export const useWebSocket = () => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    
    const newSocket = io('ws://localhost:8000', {
      auth: { token }
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  return { socket, connected };
};
```

### 2. Listen to Events

```typescript
const DashboardPage = () => {
  const { socket } = useWebSocket();
  const [junctionStatus, setJunctionStatus] = useState({});

  useEffect(() => {
    if (!socket) return;

    // Listen for junction status updates
    socket.on('junction_status', (data) => {
      setJunctionStatus(prev => ({
        ...prev,
        [data.junction_id]: data.status
      }));
    });

    // Listen for mode changes
    socket.on('mode_change', (data) => {
      toast.info(`System mode changed to ${data.new_mode}`);
    });

    // Listen for alerts
    socket.on('alert', (data) => {
      toast.warning(data.message);
    });

    return () => {
      socket.off('junction_status');
      socket.off('mode_change');
      socket.off('alert');
    };
  }, [socket]);

  return <Dashboard junctionStatus={junctionStatus} />;
};
```

---

## Performance Optimization

### 1. Memoization

```typescript
import { useMemo } from 'react';

const JunctionList = ({ junctions, filters }) => {
  const filteredJunctions = useMemo(() => {
    return junctions.filter(j => {
      if (filters.status && j.status !== filters.status) return false;
      if (filters.zone && j.zone !== filters.zone) return false;
      if (filters.search && !j.name.toLowerCase().includes(filters.search.toLowerCase())) return false;
      return true;
    });
  }, [junctions, filters]);

  return (
    <div>
      {filteredJunctions.map(junction => (
        <JunctionCard key={junction.id} junction={junction} />
      ))}
    </div>
  );
};
```

### 2. Debouncing

```typescript
import { useState, useEffect } from 'react';

const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Usage
const SearchBar = () => {
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebounce(search, 500);

  useEffect(() => {
    if (debouncedSearch) {
      // Fetch results
      fetchJunctions({ search: debouncedSearch });
    }
  }, [debouncedSearch]);

  return (
    <input
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      placeholder="Search junctions..."
    />
  );
};
```

### 3. Lazy Loading

```typescript
import { lazy, Suspense } from 'react';

const DashboardPage = lazy(() => import('./pages/dashboard/DashboardPage'));
const JunctionsPage = lazy(() => import('./pages/junctions/JunctionsPage'));
const ControlPage = lazy(() => import('./pages/control/ControlPage'));

const AppRouter = () => {
  return (
    <Suspense fallback={<Loader />}>
      <Routes>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/junctions" element={<JunctionsPage />} />
        <Route path="/control" element={<ControlPage />} />
      </Routes>
    </Suspense>
  );
};
```

---

## Testing

### 1. API Mocking

```typescript
// src/api/__mocks__/auth.api.ts
export const authAPI = {
  login: jest.fn().mockResolvedValue({
    user: { id: 1, name: 'Test User', email: 'test@test.com', role: 'admin' },
    tokens: {
      access_token: 'mock_token',
      refresh_token: 'mock_refresh',
      token_type: 'bearer',
      expires_in: 1800
    }
  }),
  
  getCurrentUser: jest.fn().mockResolvedValue({
    id: 1,
    name: 'Test User',
    email: 'test@test.com',
    role: 'admin'
  })
};
```

### 2. Component Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginPage } from './LoginPage';

test('login form submits correctly', async () => {
  render(<LoginPage />);
  
  // Fill form
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'admin@itms.com' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'admin123' }
  });
  
  // Submit
  fireEvent.click(screen.getByRole('button', { name: /login/i }));
  
  // Wait for redirect
  await waitFor(() => {
    expect(window.location.pathname).toBe('/dashboard');
  });
});
```

---

## Deployment

### 1. Build for Production

```bash
npm run build
```

### 2. Environment Variables

```env
# .env.production
VITE_API_BASE_URL=https://api.itms.com/api/v1
VITE_WS_URL=wss://api.itms.com/ws
```

### 3. Deploy to Nginx

```nginx
server {
    listen 80;
    server_name itms.com;
    
    root /var/www/itms-frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

This guide provides everything needed to integrate the frontend with your ITMS backend!
