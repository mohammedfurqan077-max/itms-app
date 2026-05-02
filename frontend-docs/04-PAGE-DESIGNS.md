# ITMS Frontend - Page Designs & Features

## Page Overview

### 1. Login Page (`/login`)
### 2. Dashboard Page (`/dashboard`)
### 3. Junctions Page (`/junctions`)
### 4. Control Page (`/control`)
### 5. Commands Page (`/commands`)
### 6. Settings Page (`/settings`)

---

## 1. Login Page

### Features
- Email and password input
- Remember me checkbox
- Login button
- Error messages
- Loading state

### Layout
```
┌─────────────────────────────────────┐
│                                     │
│          ITMS Logo                  │
│                                     │
│    ┌─────────────────────────┐     │
│    │  Email                  │     │
│    │  [________________]     │     │
│    │                         │     │
│    │  Password               │     │
│    │  [________________]     │     │
│    │                         │     │
│    │  [ ] Remember me        │     │
│    │                         │     │
│    │  [    Login    ]        │     │
│    └─────────────────────────┘     │
│                                     │
└─────────────────────────────────────┘
```

### API Calls
- `POST /auth/login`

### State Management
- Form state (email, password)
- Loading state
- Error state
- Store tokens on success
- Redirect to dashboard

---

## 2. Dashboard Page

### Features
- System overview statistics
- Junction status summary
- Recent commands
- System mode indicator
- Quick actions

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: ITMS Dashboard                    [User Menu]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Total    │  │ Online   │  │ Commands │  │ Success│ │
│  │ Junctions│  │ Junctions│  │ Today    │  │ Rate   │ │
│  │    12    │  │    10    │  │   156    │  │  98%   │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│                                                         │
│  ┌─────────────────────────┐  ┌──────────────────────┐ │
│  │ System Status           │  │ Recent Commands      │ │
│  │                         │  │                      │ │
│  │ Current Mode: Manual    │  │ 1. Set Mode - Success│ │
│  │ Active Junctions: 10    │  │ 2. Set Time - Success│ │
│  │ VIP Mode: Inactive      │  │ 3. Heartbeat - Success│ │
│  │                         │  │ 4. Get Status - Success│ │
│  │ [Change Mode]           │  │                      │ │
│  └─────────────────────────┘  └──────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Junction Status Map                              │  │
│  │                                                  │  │
│  │  [Interactive map showing junction locations]   │  │
│  │  Green = Online, Red = Offline, Yellow = Maint. │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### API Calls
- `GET /system/state` - Current system mode
- `GET /junctions/stats/overview` - Junction statistics
- `GET /commands/stats/overview` - Command statistics
- `GET /junctions?page=1&page_size=100` - All junctions for map
- `GET /commands?page=1&page_size=10` - Recent commands

### Real-time Updates
- WebSocket connection for live junction status
- Auto-refresh every 30 seconds

---

## 3. Junctions Page

### Features
- List all junctions
- Filter by status, zone
- Search by name
- Create new junction
- Edit junction
- Delete junction
- View junction details
- Pagination

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: Junction Management              [User Menu]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [+ New Junction]                                       │
│                                                         │
│  Filters:                                               │
│  Status: [All ▼]  Zone: [All ▼]  Search: [_______]     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Name              │ Status  │ Zone  │ Actions    │  │
│  ├──────────────────────────────────────────────────┤  │
│  │ Main Square      │ ● Online│ Zone A│ [Edit][Del]│  │
│  │ North Gate       │ ● Online│ Zone B│ [Edit][Del]│  │
│  │ South Plaza      │ ○ Offline│Zone A│ [Edit][Del]│  │
│  │ East Junction    │ ● Online│ Zone C│ [Edit][Del]│  │
│  │ West Junction    │ ⚠ Maint.│ Zone B│ [Edit][Del]│  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Showing 1-5 of 12    [< 1 2 3 >]                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Junction Detail Modal
```
┌─────────────────────────────────────┐
│  Junction Details          [X]      │
├─────────────────────────────────────┤
│                                     │
│  Name: Main Square Junction        │
│  Location: Main Square, Downtown   │
│  IP Address: 192.168.1.100         │
│  Device ID: RPI-001                │
│  Status: ● Online                  │
│  Zone: Zone A                      │
│  Last Seen: 2 minutes ago          │
│                                     │
│  Description:                       │
│  Primary junction at main square   │
│                                     │
│  [Send Command]  [Edit]  [Close]   │
│                                     │
└─────────────────────────────────────┘
```

### API Calls
- `GET /junctions` - List junctions (with filters)
- `GET /junctions/{id}` - Get junction details
- `POST /junctions` - Create junction
- `PUT /junctions/{id}` - Update junction
- `DELETE /junctions/{id}` - Delete junction
- `GET /junctions/stats/overview` - Statistics

---

## 4. Control Page

### Features
- Current system mode display
- Mode selector (Manual, Auto Circle, Auto Jump, Blinker, VIP)
- Lane timing controls (for manual mode)
- VIP mode controls
- Emergency stop button
- Real-time status display
- Visual traffic light representation

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: Traffic Control                  [User Menu]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────┐  ┌──────────────────────┐ │
│  │ Current Mode            │  │ System Status        │ │
│  │                         │  │                      │ │
│  │  ● MANUAL               │  │ All Systems Normal   │ │
│  │                         │  │ Last Update: 10s ago │ │
│  │  [Change Mode ▼]        │  │                      │ │
│  │    - Auto Circle        │  │ [🔴 Emergency Stop]  │ │
│  │    - Auto Jump          │  │                      │ │
│  │    - Blinker            │  │                      │ │
│  │    - VIP                │  │                      │ │
│  └─────────────────────────┘  └──────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Lane Controls (Manual Mode)                      │  │
│  │                                                  │  │
│  │  Lane 1:  [🟢] Time: [30s] [+][-]               │  │
│  │  Lane 2:  [🔴] Time: [45s] [+][-]               │  │
│  │  Lane 3:  [🔴] Time: [30s] [+][-]               │  │
│  │  Lane 4:  [🔴] Time: [45s] [+][-]               │  │
│  │                                                  │  │
│  │  Total Cycle: 150s                               │  │
│  │                                                  │  │
│  │  [Apply Changes]                                 │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ VIP Mode                                         │  │
│  │                                                  │  │
│  │  Status: ○ Inactive                              │  │
│  │                                                  │  │
│  │  Select Lanes for Green:                         │  │
│  │  [ ] Lane 1  [ ] Lane 2  [ ] Lane 3  [ ] Lane 4 │  │
│  │                                                  │  │
│  │  [Activate VIP Mode]                             │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### API Calls
- `GET /control/status` - Get current status
- `POST /control/mode` - Switch mode
- `POST /control/manual-times` - Set lane timings
- `POST /control/vip-override` - VIP mode control
- `POST /control/emergency-stop` - Emergency stop
- `GET /system/state` - Get system state

### Real-time Updates
- WebSocket for live status updates
- Auto-refresh every 5 seconds

---

## 5. Commands Page

### Features
- List all commands
- Filter by junction, type, status
- View command details
- Retry failed commands
- Cancel pending commands
- Command statistics
- Pagination

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: Command History                  [User Menu]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Total    │  │ Success  │  │ Failed   │  │ Pending│ │
│  │ Commands │  │ Commands │  │ Commands │  │ Commands│ │
│  │   1,234  │  │  1,180   │  │    45    │  │    9   │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│                                                         │
│  Filters:                                               │
│  Junction: [All ▼]  Type: [All ▼]  Status: [All ▼]     │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ID │ Type     │ Junction │ Status  │ Time │ Actions│ │
│  ├──────────────────────────────────────────────────┤  │
│  │ 123│ Set Mode │ Main Sq. │ ✓ Success│ 2m  │ [View]│ │
│  │ 122│ Set Time │ North G. │ ✓ Success│ 5m  │ [View]│ │
│  │ 121│ VIP Mode │ South P. │ ✗ Failed │ 10m │[Retry]│ │
│  │ 120│ Heartbeat│ East J.  │ ⏳ Pending│ 15m │[Cancel]│ │
│  │ 119│ Get Status│West J.  │ ✓ Success│ 20m │ [View]│ │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Showing 1-5 of 1,234    [< 1 2 3 ... 247 >]           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Command Detail Modal
```
┌─────────────────────────────────────┐
│  Command Details           [X]      │
├─────────────────────────────────────┤
│                                     │
│  ID: 123                            │
│  Type: Set Mode                     │
│  Junction: Main Square Junction    │
│  Status: ✓ Success                 │
│                                     │
│  Payload:                           │
│  {                                  │
│    "mode": "auto"                   │
│  }                                  │
│                                     │
│  Response:                          │
│  {                                  │
│    "mode": "auto",                  │
│    "timestamp": "2024-01-15..."     │
│  }                                  │
│                                     │
│  Created: 2024-01-15 10:30:00      │
│  Executed: 2024-01-15 10:30:01     │
│  Completed: 2024-01-15 10:30:02    │
│                                     │
│  Retry Count: 0 / 3                 │
│                                     │
│  [Close]                            │
│                                     │
└─────────────────────────────────────┘
```

### API Calls
- `GET /commands` - List commands (with filters)
- `GET /commands/{id}` - Get command details
- `POST /commands/{id}/retry` - Retry command
- `POST /commands/{id}/cancel` - Cancel command
- `GET /commands/stats/overview` - Statistics

---

## 6. Settings Page

### Features
- User profile
- Change password
- System preferences
- Notification settings

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  Header: Settings                         [User Menu]   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────┐  ┌──────────────────────┐ │
│  │ Profile                 │  │ Security             │ │
│  │                         │  │                      │ │
│  │ Name: [Admin User]      │  │ Change Password      │ │
│  │ Email: [admin@itms.com] │  │                      │ │
│  │ Role: Admin             │  │ Current: [_______]   │ │
│  │                         │  │ New: [_______]       │ │
│  │ [Update Profile]        │  │ Confirm: [_______]   │ │
│  │                         │  │                      │ │
│  │                         │  │ [Change Password]    │ │
│  └─────────────────────────┘  └──────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Preferences                                      │  │
│  │                                                  │  │
│  │ [ ] Auto-refresh dashboard                       │  │
│  │ [ ] Enable sound notifications                   │  │
│  │ [ ] Show junction map on dashboard               │  │
│  │                                                  │  │
│  │ Refresh Interval: [30s ▼]                        │  │
│  │                                                  │  │
│  │ [Save Preferences]                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### API Calls
- `GET /auth/me` - Get current user
- `POST /auth/change-password` - Change password

---

## Common UI Components

### Header Component
- App logo
- Current page title
- User menu (Profile, Settings, Logout)
- Notifications icon

### Sidebar Component (Optional)
- Dashboard
- Junctions
- Control
- Commands
- Settings

### Status Badge Component
- Online (Green)
- Offline (Red)
- Maintenance (Yellow)
- Error (Red with icon)

### Loading States
- Skeleton loaders for tables
- Spinner for buttons
- Progress bar for page loads

### Error States
- Error messages
- Retry buttons
- Empty states

---

## Responsive Design

### Desktop (> 1024px)
- Full layout with sidebar
- Multi-column layouts
- Large tables

### Tablet (768px - 1024px)
- Collapsible sidebar
- 2-column layouts
- Scrollable tables

### Mobile (< 768px)
- Bottom navigation
- Single column
- Card-based layouts
- Swipeable tables

---

This design provides a complete, user-friendly interface that perfectly integrates with your backend!
