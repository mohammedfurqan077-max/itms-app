#!/bin/bash

# Command Execution API Examples
# This script demonstrates all command execution endpoints

# Configuration
BASE_URL="http://localhost:8000/api/v1"
TOKEN="your_jwt_token_here"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Command Execution API Examples ===${NC}\n"

# Helper function to print section headers
print_section() {
    echo -e "\n${GREEN}=== $1 ===${NC}\n"
}

# Helper function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    echo -e "${BLUE}Request:${NC} $method $endpoint"
    if [ -n "$data" ]; then
        echo -e "${BLUE}Data:${NC} $data"
    fi
    echo ""
    
    if [ -n "$data" ]; then
        curl -X $method "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "\n\n" \
            -s | jq '.'
    else
        curl -X $method "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -w "\n\n" \
            -s | jq '.'
    fi
}

# ============================================================================
# 1. SEND COMMANDS
# ============================================================================

print_section "1. Send Commands"

# 1.1 Set Mode to Auto
echo -e "${BLUE}1.1 Set Mode to Auto${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "auto"
  },
  "execute_immediately": true
}'

# 1.2 Set Mode to Manual
echo -e "${BLUE}1.2 Set Mode to Manual${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "manual"
  },
  "execute_immediately": true
}'

# 1.3 Set Lane Timings
echo -e "${BLUE}1.3 Set Lane Timings${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_time",
  "payload": {
    "lane1": 45,
    "lane2": 30,
    "lane3": 45,
    "lane4": 30
  },
  "execute_immediately": true
}'

# 1.4 Enable VIP Mode
echo -e "${BLUE}1.4 Enable VIP Mode${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "vip_mode",
  "payload": {
    "active": true,
    "lanes_to_green": [1, 3]
  },
  "execute_immediately": true
}'

# 1.5 Disable VIP Mode
echo -e "${BLUE}1.5 Disable VIP Mode${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "vip_mode",
  "payload": {
    "active": false,
    "lanes_to_green": []
  },
  "execute_immediately": true
}'

# 1.6 Emergency Stop
echo -e "${BLUE}1.6 Emergency Stop${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "emergency_stop",
  "payload": {},
  "execute_immediately": true
}'

# 1.7 Get Status
echo -e "${BLUE}1.7 Get Status${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

# 1.8 Heartbeat
echo -e "${BLUE}1.8 Heartbeat${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "heartbeat",
  "payload": {},
  "execute_immediately": true
}'

# 1.9 Queue Command (Don't Execute Immediately)
echo -e "${BLUE}1.9 Queue Command${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "auto"
  },
  "execute_immediately": false
}'

# ============================================================================
# 2. GET COMMAND DETAILS
# ============================================================================

print_section "2. Get Command Details"

# 2.1 Get Command by ID
echo -e "${BLUE}2.1 Get Command by ID${NC}"
api_call GET "/commands/1"

# ============================================================================
# 3. LIST COMMANDS
# ============================================================================

print_section "3. List Commands"

# 3.1 List All Commands (First Page)
echo -e "${BLUE}3.1 List All Commands (First Page)${NC}"
api_call GET "/commands?page=1&page_size=10"

# 3.2 List Commands by Junction
echo -e "${BLUE}3.2 List Commands by Junction${NC}"
api_call GET "/commands?junction_id=1&page=1&page_size=10"

# 3.3 List Commands by Type
echo -e "${BLUE}3.3 List Commands by Type (set_mode)${NC}"
api_call GET "/commands?command_type=set_mode&page=1&page_size=10"

# 3.4 List Commands by Status
echo -e "${BLUE}3.4 List Commands by Status (success)${NC}"
api_call GET "/commands?status=success&page=1&page_size=10"

# 3.5 List Failed Commands
echo -e "${BLUE}3.5 List Failed Commands${NC}"
api_call GET "/commands?status=failed&page=1&page_size=10"

# 3.6 List Pending Commands
echo -e "${BLUE}3.6 List Pending Commands${NC}"
api_call GET "/commands?status=pending&page=1&page_size=10"

# 3.7 Combined Filters
echo -e "${BLUE}3.7 Combined Filters (Junction 1, set_mode, success)${NC}"
api_call GET "/commands?junction_id=1&command_type=set_mode&status=success&page=1&page_size=10"

# ============================================================================
# 4. RETRY COMMAND
# ============================================================================

print_section "4. Retry Command"

# 4.1 Retry Failed Command (Normal)
echo -e "${BLUE}4.1 Retry Failed Command (Normal)${NC}"
api_call POST "/commands/1/retry" '{
  "force": false
}'

# 4.2 Force Retry Command
echo -e "${BLUE}4.2 Force Retry Command${NC}"
api_call POST "/commands/1/retry" '{
  "force": true
}'

# ============================================================================
# 5. CANCEL COMMAND
# ============================================================================

print_section "5. Cancel Command"

# 5.1 Cancel Pending Command
echo -e "${BLUE}5.1 Cancel Pending Command${NC}"
api_call POST "/commands/1/cancel"

# ============================================================================
# 6. COMMAND STATISTICS
# ============================================================================

print_section "6. Command Statistics"

# 6.1 Get Command Statistics
echo -e "${BLUE}6.1 Get Command Statistics${NC}"
api_call GET "/commands/stats/overview"

# ============================================================================
# 7. GET PENDING COMMANDS (ADMIN ONLY)
# ============================================================================

print_section "7. Get Pending Commands (Admin Only)"

# 7.1 Get Pending Commands (Default Limit)
echo -e "${BLUE}7.1 Get Pending Commands (Default Limit)${NC}"
api_call GET "/commands/pending/list"

# 7.2 Get Pending Commands (Custom Limit)
echo -e "${BLUE}7.2 Get Pending Commands (Custom Limit: 50)${NC}"
api_call GET "/commands/pending/list?limit=50"

# ============================================================================
# 8. WORKFLOW EXAMPLES
# ============================================================================

print_section "8. Workflow Examples"

# 8.1 Complete Traffic Mode Switch Workflow
echo -e "${BLUE}8.1 Complete Traffic Mode Switch Workflow${NC}"
echo "Step 1: Get current status"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

echo "Step 2: Switch to manual mode"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "manual"
  },
  "execute_immediately": true
}'

echo "Step 3: Set custom lane timings"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_time",
  "payload": {
    "lane1": 60,
    "lane2": 30,
    "lane3": 60,
    "lane4": 30
  },
  "execute_immediately": true
}'

echo "Step 4: Verify status"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

# 8.2 VIP Mode Workflow
echo -e "${BLUE}8.2 VIP Mode Workflow${NC}"
echo "Step 1: Enable VIP mode for lanes 1 and 3"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "vip_mode",
  "payload": {
    "active": true,
    "lanes_to_green": [1, 3]
  },
  "execute_immediately": true
}'

echo "Step 2: Wait for VIP vehicle to pass (simulated)"
sleep 2

echo "Step 3: Disable VIP mode"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "vip_mode",
  "payload": {
    "active": false,
    "lanes_to_green": []
  },
  "execute_immediately": true
}'

echo "Step 4: Return to auto mode"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "auto"
  },
  "execute_immediately": true
}'

# 8.3 Error Handling Workflow
echo -e "${BLUE}8.3 Error Handling Workflow${NC}"
echo "Step 1: Send command that might fail"
RESPONSE=$(curl -X POST "$BASE_URL/commands/send" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "junction_id": 1,
      "command_type": "set_mode",
      "payload": {
        "mode": "invalid_mode"
      },
      "execute_immediately": true
    }' \
    -s)

echo "$RESPONSE" | jq '.'

COMMAND_ID=$(echo "$RESPONSE" | jq -r '.command_id')

echo "Step 2: Check command status"
api_call GET "/commands/$COMMAND_ID"

echo "Step 3: Retry if failed"
if [ "$(echo "$RESPONSE" | jq -r '.success')" = "false" ]; then
    api_call POST "/commands/$COMMAND_ID/retry" '{
      "force": false
    }'
fi

# ============================================================================
# 9. MONITORING EXAMPLES
# ============================================================================

print_section "9. Monitoring Examples"

# 9.1 Check System Health
echo -e "${BLUE}9.1 Check System Health${NC}"
echo "Get command statistics"
api_call GET "/commands/stats/overview"

echo "Get pending commands count"
api_call GET "/commands?status=pending&page=1&page_size=1"

echo "Get failed commands count"
api_call GET "/commands?status=failed&page=1&page_size=1"

# 9.2 Junction-Specific Monitoring
echo -e "${BLUE}9.2 Junction-Specific Monitoring${NC}"
echo "Get all commands for Junction 1"
api_call GET "/commands?junction_id=1&page=1&page_size=20"

echo "Get recent commands for Junction 1"
api_call GET "/commands?junction_id=1&page=1&page_size=5"

# ============================================================================
# 10. BULK OPERATIONS
# ============================================================================

print_section "10. Bulk Operations"

# 10.1 Send Commands to Multiple Junctions
echo -e "${BLUE}10.1 Send Commands to Multiple Junctions${NC}"
for junction_id in 1 2 3; do
    echo "Sending heartbeat to Junction $junction_id"
    api_call POST "/commands/send" "{
      \"junction_id\": $junction_id,
      \"command_type\": \"heartbeat\",
      \"payload\": {},
      \"execute_immediately\": true
    }"
done

# 10.2 Batch Status Check
echo -e "${BLUE}10.2 Batch Status Check${NC}"
for junction_id in 1 2 3; do
    echo "Getting status for Junction $junction_id"
    api_call POST "/commands/send" "{
      \"junction_id\": $junction_id,
      \"command_type\": \"get_status\",
      \"payload\": {},
      \"execute_immediately\": true
    }"
done

echo -e "\n${GREEN}=== Examples Complete ===${NC}\n"
echo "Note: Replace 'your_jwt_token_here' with a valid JWT token"
echo "To get a token, use the authentication endpoints first"
