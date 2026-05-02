# ITMS Backend - Data Models & TypeScript Interfaces

## TypeScript Interfaces for Frontend

### 1. User Models

```typescript
// User Role Enum
export enum UserRole {
  ADMIN = 'admin',
  JAWAN = 'jawan'
}

// User Status Enum
export enum UserStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  LOCKED = 'locked'
}

// User Interface
export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  created_at: string; // ISO 8601 date string
  updated_at: string;
  last_login?: string;
}

// Login Request
export interface LoginRequest {
  email: string;
  password: string;
}

// Login Response
export interface LoginResponse {
  user: User;
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  };
}

// Register Request
export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  role: UserRole;
}

// Change Password Request
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}
```

---

### 2. System State Models

```typescript
// System Mode Enum
export enum SystemMode {
  MANUAL = 'manual',
  AUTO_CIRCLE = 'auto_circle',
  AUTO_JUMP = 'auto_jump',
  BLINKER = 'blinker',
  VIP = 'vip'
}

// System State Interface
export interface SystemState {
  id: number;
  current_mode: SystemMode;
  last_updated_by: number;
  junction_id?: number;
  mode_metadata?: string; // JSON string
  updated_at: string;
  created_at: string;
  updated_by_name?: string;
  junction_name?: string;
}

// Update Mode Request
export interface UpdateModeRequest {
  new_mode: SystemMode;
  junction_id?: number;
  mode_metadata?: Record<string, any>;
}

// Current Mode Response
export interface CurrentModeResponse {
  current_mode: SystemMode;
}
```

---

### 3. Junction Models

```typescript
// Junction Status Enum
export enum JunctionStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  MAINTENANCE = 'maintenance',
  ERROR = 'error'
}

// Junction Interface
export interface Junction {
  id: number;
  name: string;
  location?: string;
  ip_address: string;
  device_id?: string;
  status: JunctionStatus;
  last_seen?: string;
  description?: string;
  zone?: string;
  config_metadata?: string; // JSON string
  created_at: string;
  updated_at: string;
}

// Create Junction Request
export interface CreateJunctionRequest {
  name: string;
  location?: string;
  ip_address: string;
  device_id?: string;
  description?: string;
  zone?: string;
  config_metadata?: Record<string, any>;
}

// Update Junction Request
export interface UpdateJunctionRequest {
  name?: string;
  location?: string;
  ip_address?: string;
  device_id?: string;
  description?: string;
  zone?: string;
  config_metadata?: Record<string, any>;
}

// Update Junction Status Request
export interface UpdateJunctionStatusRequest {
  status: JunctionStatus;
}

// Junction List Response
export interface JunctionListResponse {
  junctions: Junction[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Junction Statistics
export interface JunctionStats {
  total_junctions: number;
  online_junctions: number;
  offline_junctions: number;
  maintenance_junctions: number;
  error_junctions: number;
  junctions_by_zone: Record<string, number>;
  junctions_by_status: Record<string, number>;
}
```

---

### 4. Command Models

```typescript
// Command Type Enum
export enum CommandType {
  SET_MODE = 'set_mode',
  SET_TIME = 'set_time',
  VIP_MODE = 'vip_mode',
  EMERGENCY_STOP = 'emergency_stop',
  HEARTBEAT = 'heartbeat',
  GET_STATUS = 'get_status'
}

// Command Status Enum
export enum CommandStatus {
  PENDING = 'pending',
  EXECUTING = 'executing',
  SUCCESS = 'success',
  FAILED = 'failed',
  TIMEOUT = 'timeout',
  CANCELLED = 'cancelled'
}

// Command Interface
export interface Command {
  id: number;
  junction_id?: number;
  command_type: CommandType;
  payload?: string; // JSON string
  status: CommandStatus;
  response?: string; // JSON string
  error_message?: string;
  created_by?: number;
  retry_count: number;
  max_retries: number;
  created_at: string;
  executed_at?: string;
  completed_at?: string;
}

// Send Command Request
export interface SendCommandRequest {
  junction_id?: number;
  command_type: CommandType;
  payload?: Record<string, any>;
  execute_immediately?: boolean;
}

// Command Execution Result
export interface CommandExecutionResult {
  command_id: number;
  success: boolean;
  message: string;
  status: CommandStatus;
  response_data?: Record<string, any>;
  error?: string;
  executed_at?: string;
}

// Command List Response
export interface CommandListResponse {
  commands: Command[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Command Statistics
export interface CommandStats {
  total_commands: number;
  pending_commands: number;
  executing_commands: number;
  success_commands: number;
  failed_commands: number;
  timeout_commands: number;
  cancelled_commands: number;
  commands_by_type: Record<string, number>;
  commands_by_junction: Record<number, number>;
  average_execution_time?: number;
}

// Retry Command Request
export interface RetryCommandRequest {
  force?: boolean;
}
```

---

### 5. Control System Models

```typescript
// Lane State Enum
export enum LaneState {
  RED = 'red',
  YELLOW = 'yellow',
  GREEN = 'green'
}

// Control Mode Enum
export enum ControlMode {
  AUTO = 'auto',
  MANUAL = 'manual',
  VIP = 'vip',
  EMERGENCY = 'emergency'
}

// Switch Mode Request
export interface SwitchModeRequest {
  mode: ControlMode;
}

// Set Manual Times Request
export interface SetManualTimesRequest {
  lane1: number;
  lane2: number;
  lane3: number;
  lane4: number;
}

// VIP Override Request
export interface VIPOverrideRequest {
  active: boolean;
  lanes_to_green: number[];
}

// Control Status Response
export interface ControlStatusResponse {
  success: boolean;
  data: {
    mode: ControlMode;
    lane_states: {
      lane1: LaneState;
      lane2: LaneState;
      lane3: LaneState;
      lane4: LaneState;
    };
    timings: {
      lane1: number;
      lane2: number;
      lane3: number;
      lane4: number;
    };
    vip_active: boolean;
    emergency_stop: boolean;
  };
}

// Control Response
export interface ControlResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
  error?: string;
}
```

---

### 6. Common Models

```typescript
// API Response Wrapper
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Pagination Params
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

// Filter Params for Junctions
export interface JunctionFilterParams extends PaginationParams {
  status?: JunctionStatus;
  zone?: string;
  search?: string;
}

// Filter Params for Commands
export interface CommandFilterParams extends PaginationParams {
  junction_id?: number;
  command_type?: CommandType;
  status?: CommandStatus;
}

// Error Response
export interface ErrorResponse {
  success: false;
  error: string;
  error_code?: string;
  details?: any;
}

// Validation Error
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
```

---

### 7. WebSocket Models (Future)

```typescript
// WebSocket Message Type
export enum WSMessageType {
  JUNCTION_STATUS = 'junction_status',
  MODE_CHANGE = 'mode_change',
  VIP_MODE_ACTIVE = 'vip_mode_active',
  ALERT = 'alert',
  COMMAND_UPDATE = 'command_update'
}

// WebSocket Message
export interface WSMessage {
  type: WSMessageType;
  data: any;
  timestamp: string;
}

// Junction Status Update
export interface JunctionStatusUpdate {
  junction_id: number;
  status: JunctionStatus;
  last_seen: string;
}

// Mode Change Update
export interface ModeChangeUpdate {
  old_mode: SystemMode;
  new_mode: SystemMode;
  changed_by: number;
  timestamp: string;
}
```

---

## Example Usage in Frontend

### React/TypeScript Example

```typescript
import axios from 'axios';
import { LoginRequest, LoginResponse, User } from './types';

// API Client
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login function
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/auth/login', credentials);
  return response.data;
};

// Get current user
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/auth/me');
  return response.data;
};

// Get junctions
export const getJunctions = async (params?: JunctionFilterParams): Promise<JunctionListResponse> => {
  const response = await api.get<JunctionListResponse>('/junctions', { params });
  return response.data;
};

// Send command
export const sendCommand = async (request: SendCommandRequest): Promise<CommandExecutionResult> => {
  const response = await api.post<CommandExecutionResult>('/commands/send', request);
  return response.data;
};
```

---

## Validation Rules

### User
- **name**: 2-100 characters
- **email**: Valid email format, unique
- **password**: Minimum 8 characters

### Junction
- **name**: 1-100 characters, unique
- **ip_address**: Valid IPv4 or IPv6, unique
- **device_id**: Optional, unique if provided

### Command
- **command_type**: Must be one of the enum values
- **payload**: Valid JSON for the command type

### Control
- **lane timings**: 5-120 seconds per lane
- **total cycle time**: 60-300 seconds
