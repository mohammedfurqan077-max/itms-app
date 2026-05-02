#!/bin/bash

# Junction Management API - Example Requests
# This script demonstrates all junction management endpoints

BASE_URL="http://localhost:8000/api/v1"

echo "========================================="
echo "Junction Management API - Examples"
echo "========================================="
echo ""

# Step 1: Login as admin
echo "1. Login as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@itms.com",
    "password": "admin123"
  }')

ADMIN_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.tokens.access_token')
echo "✅ Admin token obtained"
echo ""

# Step 2: Create Junction
echo "2. Create new junction..."
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/junctions" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Junction 1",
    "location": "Test Location, City Center",
    "ip_address": "192.168.1.200",
    "device_id": "RPI-TEST-001",
    "description": "Test junction for API demonstration",
    "zone": "Test Zone",
    "config_metadata": "{\"lanes\": 4, \"has_camera\": true}"
  }')

JUNCTION_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
echo "Response:"
echo $CREATE_RESPONSE | jq '.'
echo ""

# Step 3: List Junctions
echo "3. List all junctions (page 1, 10 items)..."
curl -s -X GET "$BASE_URL/junctions?page=1&page_size=10" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Step 4: Get Junction by ID
echo "4. Get junction by ID ($JUNCTION_ID)..."
curl -s -X GET "$BASE_URL/junctions/$JUNCTION_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Step 5: Update Junction
echo "5. Update junction..."
curl -s -X PUT "$BASE_URL/junctions/$JUNCTION_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Updated Location, City Center",
    "description": "Updated description"
  }' | jq '.'
echo ""

# Step 6: Update Junction Status
echo "6. Update junction status to 'online'..."
curl -s -X PATCH "$BASE_URL/junctions/$JUNCTION_ID/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "online"
  }' | jq '.'
echo ""

# Step 7: Process Heartbeat
echo "7. Process heartbeat from device..."
curl -s -X POST "$BASE_URL/junctions/heartbeat" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "RPI-TEST-001",
    "status": "online",
    "metadata": {
      "cpu_temp": 45.2,
      "uptime": 86400
    }
  }' | jq '.'
echo ""

# Step 8: Get Junction Statistics
echo "8. Get junction statistics..."
curl -s -X GET "$BASE_URL/junctions/stats/overview" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Step 9: Filter Junctions by Status
echo "9. Filter junctions by status (online)..."
curl -s -X GET "$BASE_URL/junctions?status=online" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Step 10: Filter Junctions by Zone
echo "10. Filter junctions by zone (Test Zone)..."
curl -s -X GET "$BASE_URL/junctions?zone=Test%20Zone" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Step 11: Search Junctions
echo "11. Search junctions (search: 'Test')..."
curl -s -X GET "$BASE_URL/junctions?search=Test" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Step 12: Check Offline Junctions
echo "12. Check offline junctions (timeout: 5 minutes)..."
curl -s -X GET "$BASE_URL/junctions/health/check-offline?timeout_minutes=5" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.'
echo ""

# Step 13: Update Status to Maintenance
echo "13. Update junction status to 'maintenance'..."
curl -s -X PATCH "$BASE_URL/junctions/$JUNCTION_ID/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "maintenance"
  }' | jq '.'
echo ""

# Step 14: Delete Junction
echo "14. Delete junction..."
curl -s -X DELETE "$BASE_URL/junctions/$JUNCTION_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
echo "✅ Junction deleted (204 No Content)"
echo ""

echo "========================================="
echo "✅ All junction API examples completed!"
echo "========================================="
