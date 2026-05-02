#!/bin/bash

# Integration Test Script for SystemState + Control Service
# This script tests the complete integration flow

set -e

echo "=========================================="
echo "ITMS Integration Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8000/api/v1"

# Check if backend is running
echo "Checking if backend is running..."
if ! curl -s "$BASE_URL/../health" > /dev/null; then
    echo -e "${RED}❌ Backend is not running!${NC}"
    echo "Please start the backend: uvicorn app.main:app --reload"
    exit 1
fi
echo -e "${GREEN}✅ Backend is running${NC}"
echo ""

# Check if mock control system is running
echo "Checking if mock control system is running..."
if ! curl -s "http://localhost:5000/health" > /dev/null; then
    echo -e "${YELLOW}⚠️  Mock control system is not running!${NC}"
    echo "Please start it: python tests/mock_control_system.py"
    echo "Continuing anyway (some tests will fail)..."
else
    echo -e "${GREEN}✅ Mock control system is running${NC}"
fi
echo ""

# Login as admin
echo "Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@itms.com","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.tokens.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Login failed!${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi
echo -e "${GREEN}✅ Logged in successfully${NC}"
echo ""

# Test 1: Get current state
echo "=========================================="
echo "Test 1: Get Current State"
echo "=========================================="
CURRENT_STATE=$(curl -s -X GET "$BASE_URL/system/state" \
  -H "Authorization: Bearer $TOKEN")

CURRENT_MODE=$(echo $CURRENT_STATE | jq -r '.current_mode')
echo "Current mode: $CURRENT_MODE"
echo -e "${GREEN}✅ Test 1 passed${NC}"
echo ""

# Test 2: Switch mode to auto_circle
echo "=========================================="
echo "Test 2: Switch Mode to auto_circle"
echo "=========================================="
SWITCH_RESPONSE=$(curl -s -X POST "$BASE_URL/control/switch_mode" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"auto_circle"}')

SUCCESS=$(echo $SWITCH_RESPONSE | jq -r '.success')
PREVIOUS_MODE=$(echo $SWITCH_RESPONSE | jq -r '.previous_mode')
NEW_MODE=$(echo $SWITCH_RESPONSE | jq -r '.current_mode')

echo "Success: $SUCCESS"
echo "Previous mode: $PREVIOUS_MODE"
echo "New mode: $NEW_MODE"

if [ "$SUCCESS" == "true" ]; then
    echo -e "${GREEN}✅ Test 2 passed${NC}"
else
    ERROR=$(echo $SWITCH_RESPONSE | jq -r '.error')
    echo -e "${RED}❌ Test 2 failed: $ERROR${NC}"
fi
echo ""

# Test 3: Verify state updated
echo "=========================================="
echo "Test 3: Verify State Updated"
echo "=========================================="
UPDATED_STATE=$(curl -s -X GET "$BASE_URL/system/state" \
  -H "Authorization: Bearer $TOKEN")

UPDATED_MODE=$(echo $UPDATED_STATE | jq -r '.current_mode')
echo "Updated mode: $UPDATED_MODE"

if [ "$UPDATED_MODE" == "auto_circle" ]; then
    echo -e "${GREEN}✅ Test 3 passed - State updated correctly${NC}"
else
    echo -e "${RED}❌ Test 3 failed - State not updated${NC}"
fi
echo ""

# Test 4: Set manual times
echo "=========================================="
echo "Test 4: Set Manual Times"
echo "=========================================="
MANUAL_RESPONSE=$(curl -s -X POST "$BASE_URL/control/manual_times" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lane1":30,"lane2":45,"lane3":30,"lane4":45}')

SUCCESS=$(echo $MANUAL_RESPONSE | jq -r '.success')
echo "Success: $SUCCESS"

if [ "$SUCCESS" == "true" ]; then
    echo -e "${GREEN}✅ Test 4 passed${NC}"
else
    ERROR=$(echo $MANUAL_RESPONSE | jq -r '.error')
    echo -e "${RED}❌ Test 4 failed: $ERROR${NC}"
fi
echo ""

# Test 5: Verify mode changed to manual
echo "=========================================="
echo "Test 5: Verify Mode Changed to Manual"
echo "=========================================="
MANUAL_STATE=$(curl -s -X GET "$BASE_URL/system/state" \
  -H "Authorization: Bearer $TOKEN")

MANUAL_MODE=$(echo $MANUAL_STATE | jq -r '.current_mode')
echo "Current mode: $MANUAL_MODE"

if [ "$MANUAL_MODE" == "manual" ]; then
    echo -e "${GREEN}✅ Test 5 passed - Mode changed to manual${NC}"
else
    echo -e "${RED}❌ Test 5 failed - Mode not changed${NC}"
fi
echo ""

# Test 6: VIP Override
echo "=========================================="
echo "Test 6: VIP Override"
echo "=========================================="
VIP_RESPONSE=$(curl -s -X POST "$BASE_URL/control/vip_override" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active":true,"lanes_to_green":[2]}')

SUCCESS=$(echo $VIP_RESPONSE | jq -r '.success')
echo "Success: $SUCCESS"

if [ "$SUCCESS" == "true" ]; then
    echo -e "${GREEN}✅ Test 6 passed${NC}"
else
    ERROR=$(echo $VIP_RESPONSE | jq -r '.error')
    echo -e "${RED}❌ Test 6 failed: $ERROR${NC}"
fi
echo ""

# Test 7: Verify VIP mode
echo "=========================================="
echo "Test 7: Verify VIP Mode"
echo "=========================================="
VIP_STATE=$(curl -s -X GET "$BASE_URL/system/state" \
  -H "Authorization: Bearer $TOKEN")

VIP_MODE=$(echo $VIP_STATE | jq -r '.current_mode')
echo "Current mode: $VIP_MODE"

if [ "$VIP_MODE" == "vip" ]; then
    echo -e "${GREEN}✅ Test 7 passed - VIP mode activated${NC}"
else
    echo -e "${RED}❌ Test 7 failed - VIP mode not activated${NC}"
fi
echo ""

# Test 8: Deactivate VIP
echo "=========================================="
echo "Test 8: Deactivate VIP"
echo "=========================================="
DEACTIVATE_RESPONSE=$(curl -s -X POST "$BASE_URL/control/vip_override" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active":false}')

SUCCESS=$(echo $DEACTIVATE_RESPONSE | jq -r '.success')
echo "Success: $SUCCESS"

if [ "$SUCCESS" == "true" ]; then
    echo -e "${GREEN}✅ Test 8 passed${NC}"
else
    ERROR=$(echo $DEACTIVATE_RESPONSE | jq -r '.error')
    echo -e "${RED}❌ Test 8 failed: $ERROR${NC}"
fi
echo ""

# Test 9: Test authorization (jawan cannot switch mode)
echo "=========================================="
echo "Test 9: Authorization Test (Jawan)"
echo "=========================================="
JAWAN_LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"jawan@itms.com","password":"jawan123"}')

JAWAN_TOKEN=$(echo $JAWAN_LOGIN | jq -r '.tokens.access_token')

JAWAN_SWITCH=$(curl -s -X POST "$BASE_URL/control/switch_mode" \
  -H "Authorization: Bearer $JAWAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"blinker"}')

# Should fail with 403
if echo $JAWAN_SWITCH | grep -q "403\|Forbidden\|Permission denied"; then
    echo -e "${GREEN}✅ Test 9 passed - Jawan correctly denied${NC}"
else
    echo -e "${RED}❌ Test 9 failed - Jawan should not be able to switch mode${NC}"
fi
echo ""

# Test 10: Get control status
echo "=========================================="
echo "Test 10: Get Control Status"
echo "=========================================="
STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/control/status" \
  -H "Authorization: Bearer $TOKEN")

SUCCESS=$(echo $STATUS_RESPONSE | jq -r '.success')
echo "Success: $SUCCESS"

if [ "$SUCCESS" == "true" ]; then
    echo -e "${GREEN}✅ Test 10 passed${NC}"
else
    echo -e "${YELLOW}⚠️  Test 10 failed (mock control system may not be running)${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "All integration tests completed!"
echo ""
echo "Next steps:"
echo "1. Review the logs in the backend"
echo "2. Check the database: make db-shell"
echo "3. Run: SELECT * FROM system_state;"
echo ""
echo -e "${GREEN}✅ Integration testing complete!${NC}"
