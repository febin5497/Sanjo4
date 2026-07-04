#!/bin/bash

# ==============================================
# COMPREHENSIVE SYSTEM TEST SCRIPT
# Tests all API endpoints and collects issues
# ==============================================

echo "=========================================="
echo "CONSTRUCTION MANAGEMENT SYSTEM - FULL TEST"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
PASSED=0
FAILED=0
ERRORS=()

# Test function
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4

    echo -n "Testing: $description ... "

    if [ -z "$data" ]; then
        response=$(curl -s -X "$method" "http://localhost:5000/api$endpoint" \
            -H "Content-Type: application/json" \
            -w "\n%{http_code}")
    else
        response=$(curl -s -X "$method" "http://localhost:5000/api$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -w "\n%{http_code}")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ] || [ "$http_code" = "204" ]; then
        echo -e "${GREEN}✓ PASS (HTTP $http_code)${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL (HTTP $http_code)${NC}"
        ((FAILED++))
        ERRORS+=("[$description] HTTP $http_code - $endpoint")
        echo "  Response: $(echo $body | head -c 100)..."
    fi
    echo ""
}

# ==============================================
# 1. TEST HEALTH & BASIC CONNECTIVITY
# ==============================================
echo -e "${YELLOW}=== 1. HEALTH & CONNECTIVITY ===${NC}"
echo ""

test_endpoint "GET" "/" "" "Root endpoint"
test_endpoint "GET" "/health" "" "Health check"
test_endpoint "GET" "/api/health" "" "API health check"

# ==============================================
# 2. TEST AUTHENTICATION
# ==============================================
echo -e "${YELLOW}=== 2. AUTHENTICATION ===${NC}"
echo ""

# Try login with default credentials
LOGIN_DATA='{"email":"admin@example.com","password":"admin123"}'
test_endpoint "POST" "/auth/login" "$LOGIN_DATA" "Login endpoint"

# Get token from login (if successful)
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:5000/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "$LOGIN_DATA")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}WARNING: Could not obtain authentication token. Remaining tests may fail.${NC}"
    echo "Login response: $LOGIN_RESPONSE"
    echo ""
    TOKEN="test-token"
fi

# ==============================================
# 3. TEST PROJECTS ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 3. PROJECTS MODULE ===${NC}"
echo ""

test_endpoint "GET" "/projects" "" "List projects"
test_endpoint "GET" "/projects/1" "" "Get project by ID"

PROJECT_DATA='{"name":"Test Project","location":"Test Location","budget":100000,"start_date":"2026-04-01","end_date":"2026-12-31"}'
test_endpoint "POST" "/projects" "$PROJECT_DATA" "Create project"

# ==============================================
# 4. TEST STAFF ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 4. STAFF MODULE ===${NC}"
echo ""

test_endpoint "GET" "/staff" "" "List staff"
test_endpoint "GET" "/staff/1" "" "Get staff by ID"

STAFF_DATA='{"name":"John Doe","personal_phone":"9876543210","joining_date":"2026-04-01","role":"Engineer","salary":50000,"pf":12,"esi":0.75}'
test_endpoint "POST" "/staff" "$STAFF_DATA" "Create staff member"

# ==============================================
# 5. TEST ATTENDANCE ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 5. ATTENDANCE MODULE ===${NC}"
echo ""

test_endpoint "GET" "/attendance" "" "List attendance records"
test_endpoint "GET" "/attendance/reports" "" "Get attendance reports"

PUNCH_DATA='{"staff_id":1,"type":"punch_in","timestamp":"2026-04-01T09:00:00"}'
test_endpoint "POST" "/attendance/punch-in" "$PUNCH_DATA" "Punch in"

# ==============================================
# 6. TEST FINANCE ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 6. FINANCE MODULE ===${NC}"
echo ""

test_endpoint "GET" "/finance/summary" "" "Finance summary"
test_endpoint "GET" "/finance/transactions" "" "List transactions"
test_endpoint "GET" "/finance/invoices" "" "List invoices"
test_endpoint "GET" "/finance/budgets" "" "List budgets"

TRANSACTION_DATA='{"type":"expense","amount":5000,"category":"Materials","date":"2026-04-01"}'
test_endpoint "POST" "/finance/transactions" "$TRANSACTION_DATA" "Create transaction"

# ==============================================
# 7. TEST PROCUREMENT ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 7. PROCUREMENT MODULE ===${NC}"
echo ""

test_endpoint "GET" "/procurement/indents" "" "List indents"
test_endpoint "GET" "/procurement/purchases" "" "List purchase orders"
test_endpoint "GET" "/procurement/suppliers" "" "List suppliers"

PURCHASE_DATA='{"supplier_id":1,"items":[{"name":"Cement","quantity":100,"price":500}],"total":50000,"date":"2026-04-01"}'
test_endpoint "POST" "/procurement/purchases" "$PURCHASE_DATA" "Create purchase order"

# ==============================================
# 8. TEST ADMINISTRATION ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 8. ADMINISTRATION MODULE ===${NC}"
echo ""

test_endpoint "GET" "/admin/users" "" "List users"
test_endpoint "GET" "/admin/roles" "" "List roles"
test_endpoint "GET" "/admin/permissions" "" "List permissions"
test_endpoint "GET" "/admin/activity-logs" "" "Activity logs"

# ==============================================
# 9. TEST STORE/MATERIALS ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 9. STORE/MATERIALS MODULE ===${NC}"
echo ""

test_endpoint "GET" "/materials" "" "List materials"
test_endpoint "GET" "/store" "" "List store items"

MATERIAL_DATA='{"name":"Cement","category":"Materials","quantity":1000,"unit":"bags","price":500}'
test_endpoint "POST" "/materials" "$MATERIAL_DATA" "Create material"

# ==============================================
# 10. TEST SETTINGS ENDPOINTS
# ==============================================
echo -e "${YELLOW}=== 10. SETTINGS MODULE ===${NC}"
echo ""

test_endpoint "GET" "/settings" "" "Get settings"

SETTINGS_DATA='{"email_notifications":true,"push_notifications":true}'
test_endpoint "PUT" "/settings" "$SETTINGS_DATA" "Update settings"

# ==============================================
# SUMMARY
# ==============================================
echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}FAILED ENDPOINTS:${NC}"
    printf '%s\n' "${ERRORS[@]}"
    echo ""
fi

echo "Total tests: $((PASSED + FAILED))"
echo "Success rate: $(( (PASSED * 100) / (PASSED + FAILED) ))%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED - See errors above${NC}"
    exit 1
fi
