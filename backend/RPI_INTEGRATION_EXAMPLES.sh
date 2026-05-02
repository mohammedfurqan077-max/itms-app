#!/bin/bash

# Raspberry Pi Integration - Example Requests
# This script demonstrates command execution with real RPi devices

# Configuration
BASE_URL="http://localhost:8000/api/v1"
TOKEN="your_jwt_token_here"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Raspberry Pi Integration Examples ===${NC}\n"

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
# 1. SETUP - Update Junction IP Addresses
# ============================================================================

print_section "1. Setup Junction IP Addresses"

echo -e "${YELLOW}Update junctions with real RPi IP addresses${NC}"

# Junction 1 - Main Square
echo -e "${BLUE}1.1 Update Junction 1 IP Address${NC}"
api_call PUT "/junctions/1" '{
  "ip_address": "192.168.1.100"
}'

# Junction 2 - North Gate
echo -e "${BLUE}1.2 Update Junction 2 IP Address${NC}"
api_call PUT "/junctions/2" '{
  "ip_address": "192.168.1.101"
}'

# Junction 3 - South Plaza
echo -e "${BLUE}1.3 Update Junction 3 IP Address${NC}"
api_call PUT "/junctions/3" '{
  "ip_address": "192.168.1.102"
}'

# ============================================================================
# 2. TEST CONNECTIVITY - Heartbeat Commands
# ============================================================================

print_section "2. Test Connectivity with Heartbeat"

echo -e "${YELLOW}Send heartbeat to all junctions to test connectivity${NC}"

# Heartbeat to Junction 1
echo -e "${BLUE}2.1 Heartbeat to Junction 1${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "heartbeat",
  "payload": {},
  "execute_immediately": true
}'

# Heartbeat to Junction 2
echo -e "${BLUE}2.2 Heartbeat to Junction 2${NC}"
api_call POST "/commands/send" '{
  "junction_id": 2,
  "command_type": "heartbeat",
  "payload": {},
  "execute_immediately": true
}'

# Heartbeat to Junction 3
echo -e "${BLUE}2.3 Heartbeat to Junction 3${NC}"
api_call POST "/commands/send" '{
  "junction_id": 3,
  "command_type": "heartbeat",
  "payload": {},
  "execute_immediately": true
}'

# ============================================================================
# 3. SET MODE COMMANDS
# ============================================================================

print_section "3. Set Mode Commands"

# Set to Auto Mode
echo -e "${BLUE}3.1 Set Junction 1 to Auto Mode${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "auto"
  },
  "execute_immediately": true
}'

# Set to Manual Mode
echo -e "${BLUE}3.2 Set Junction 1 to Manual Mode${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "manual"
  },
  "execute_immediately": true
}'

# Set to Blinker Mode
echo -e "${BLUE}3.3 Set Junction 2 to Blinker Mode${NC}"
api_call POST "/commands/send" '{
  "junction_id": 2,
  "command_type": "set_mode",
  "payload": {
    "mode": "blinker"
  },
  "execute_immediately": true
}'

# ============================================================================
# 4. SET MANUAL TIMES
# ============================================================================

print_section "4. Set Manual Lane Timings"

# Standard timings
echo -e "${BLUE}4.1 Set Standard Timings (30s each)${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_time",
  "payload": {
    "lane1": 30,
    "lane2": 30,
    "lane3": 30,
    "lane4": 30
  },
  "execute_immediately": true
}'

# Peak hour timings
echo -e "${BLUE}4.2 Set Peak Hour Timings${NC}"
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

# Custom timings
echo -e "${BLUE}4.3 Set Custom Timings${NC}"
api_call POST "/commands/send" '{
  "junction_id": 2,
  "command_type": "set_time",
  "payload": {
    "lane1": 60,
    "lane2": 20,
    "lane3": 40,
    "lane4": 30
  },
  "execute_immediately": true
}'

# ============================================================================
# 5. VIP MODE COMMANDS
# ============================================================================

print_section "5. VIP Mode Commands"

# Activate VIP mode for lanes 1 and 3
echo -e "${BLUE}5.1 Activate VIP Mode (Lanes 1 & 3)${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "vip_mode",
  "payload": {
    "active": true,
    "lanes_to_green": [1, 3]
  },
  "execute_immediately": true
}'

# Wait for VIP vehicle to pass
echo -e "${YELLOW}Waiting 5 seconds for VIP vehicle to pass...${NC}"
sleep 5

# Deactivate VIP mode
echo -e "${BLUE}5.2 Deactivate VIP Mode${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "vip_mode",
  "payload": {
    "active": false,
    "lanes_to_green": []
  },
  "execute_immediately": true
}'

# VIP mode for different lanes
echo -e "${BLUE}5.3 VIP Mode for Lanes 2 & 4${NC}"
api_call POST "/commands/send" '{
  "junction_id": 2,
  "command_type": "vip_mode",
  "payload": {
    "active": true,
    "lanes_to_green": [2, 4]
  },
  "execute_immediately": true
}'

# ============================================================================
# 6. GET STATUS COMMANDS
# ============================================================================

print_section "6. Get Status Commands"

# Get status from Junction 1
echo -e "${BLUE}6.1 Get Status from Junction 1${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

# Get status from Junction 2
echo -e "${BLUE}6.2 Get Status from Junction 2${NC}"
api_call POST "/commands/send" '{
  "junction_id": 2,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

# Get status from Junction 3
echo -e "${BLUE}6.3 Get Status from Junction 3${NC}"
api_call POST "/commands/send" '{
  "junction_id": 3,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

# ============================================================================
# 7. EMERGENCY STOP
# ============================================================================

print_section "7. Emergency Stop"

echo -e "${RED}WARNING: This will stop all traffic at the junction!${NC}"
echo -e "${YELLOW}Uncomment the following line to execute emergency stop${NC}"

# Uncomment to execute
# echo -e "${BLUE}7.1 Emergency Stop at Junction 1${NC}"
# api_call POST "/commands/send" '{
#   "junction_id": 1,
#   "command_type": "emergency_stop",
#   "payload": {},
#   "execute_immediately": true
# }'

# ============================================================================
# 8. COMMAND HISTORY
# ============================================================================

print_section "8. View Command History"

# Get recent commands
echo -e "${BLUE}8.1 Get Recent Commands${NC}"
api_call GET "/commands?page=1&page_size=10"

# Get commands for specific junction
echo -e "${BLUE}8.2 Get Commands for Junction 1${NC}"
api_call GET "/commands?junction_id=1&page=1&page_size=10"

# Get failed commands
echo -e "${BLUE}8.3 Get Failed Commands${NC}"
api_call GET "/commands?status=failed&page=1&page_size=10"

# Get success commands
echo -e "${BLUE}8.4 Get Successful Commands${NC}"
api_call GET "/commands?status=success&page=1&page_size=10"

# ============================================================================
# 9. COMMAND STATISTICS
# ============================================================================

print_section "9. Command Statistics"

# Get overall statistics
echo -e "${BLUE}9.1 Get Command Statistics${NC}"
api_call GET "/commands/stats/overview"

# ============================================================================
# 10. RETRY FAILED COMMANDS
# ============================================================================

print_section "10. Retry Failed Commands"

echo -e "${YELLOW}First, get a failed command ID from the history${NC}"

# Example: Retry command with ID 123
# echo -e "${BLUE}10.1 Retry Failed Command${NC}"
# api_call POST "/commands/123/retry" '{
#   "force": false
# }'

# ============================================================================
# 11. COMPLETE WORKFLOW EXAMPLE
# ============================================================================

print_section "11. Complete Workflow Example"

echo -e "${YELLOW}Scenario: Morning peak hour traffic management${NC}"

# Step 1: Check current status
echo -e "${BLUE}Step 1: Check current status${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

# Step 2: Switch to manual mode
echo -e "${BLUE}Step 2: Switch to manual mode${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "set_mode",
  "payload": {
    "mode": "manual"
  },
  "execute_immediately": true
}'

# Step 3: Set peak hour timings
echo -e "${BLUE}Step 3: Set peak hour timings${NC}"
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

# Step 4: Verify new status
echo -e "${BLUE}Step 4: Verify new status${NC}"
api_call POST "/commands/send" '{
  "junction_id": 1,
  "command_type": "get_status",
  "payload": {},
  "execute_immediately": true
}'

# ============================================================================
# 12. MULTI-JUNCTION COORDINATION
# ============================================================================

print_section "12. Multi-Junction Coordination"

echo -e "${YELLOW}Scenario: Coordinate multiple junctions for VIP convoy${NC}"

# Set all junctions to VIP mode
for junction_id in 1 2 3; do
    echo -e "${BLUE}Activating VIP mode at Junction $junction_id${NC}"
    api_call POST "/commands/send" "{
      \"junction_id\": $junction_id,
      \"command_type\": \"vip_mode\",
      \"payload\": {
        \"active\": true,
        \"lanes_to_green\": [1, 3]
      },
      \"execute_immediately\": true
    }"
    sleep 1
done

echo -e "${YELLOW}Waiting 10 seconds for convoy to pass...${NC}"
sleep 10

# Deactivate VIP mode at all junctions
for junction_id in 1 2 3; do
    echo -e "${BLUE}Deactivating VIP mode at Junction $junction_id${NC}"
    api_call POST "/commands/send" "{
      \"junction_id\": $junction_id,
      \"command_type\": \"vip_mode\",
      \"payload\": {
        \"active\": false,
        \"lanes_to_green\": []
      },
      \"execute_immediately\": true
    }"
    sleep 1
done

# Return all junctions to auto mode
for junction_id in 1 2 3; do
    echo -e "${BLUE}Returning Junction $junction_id to auto mode${NC}"
    api_call POST "/commands/send" "{
      \"junction_id\": $junction_id,
      \"command_type\": \"set_mode\",
      \"payload\": {
        \"mode\": \"auto\"
      },
      \"execute_immediately\": true
    }"
    sleep 1
done

echo -e "\n${GREEN}=== Examples Complete ===${NC}\n"
echo -e "${YELLOW}Note: Replace 'your_jwt_token_here' with a valid JWT token${NC}"
echo -e "${YELLOW}To get a token, use the authentication endpoints first${NC}"
echo -e "${YELLOW}Update junction IP addresses to match your RPi devices${NC}"
