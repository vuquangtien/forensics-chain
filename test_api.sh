#!/bin/bash
# API Testing Script - Forensic Chain
# Complete demonstration of all API endpoints with realistic data

BASE_URL="http://localhost:5000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_step() {
    echo -e "\n${YELLOW}[STEP $1]${NC} $2"
    echo "----------------------------------------"
}

print_success() {
    echo -e "${GREEN}✓ SUCCESS:${NC} $1"
}

print_error() {
    echo -e "${RED}✗ ERROR:${NC} $1"
}

# Check if server is running
check_server() {
    print_header "Checking API Server Status"
    response=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/health)
    if [ $response -eq 200 ]; then
        print_success "API server is running at $BASE_URL"
    else
        print_error "API server is not responding. Please start it with: python api/app.py"
        exit 1
    fi
}

# Test 1: Register Participants
test_participants() {
    print_header "TEST 1: PARTICIPANT REGISTRATION"
    
    print_step "1.1" "Register Investigator"
    curl -s -X POST $BASE_URL/api/participants \
        -H "Content-Type: application/json" \
        -d '{
            "participant_id": "INV-001",
            "name": "Detective John Smith",
            "role": "investigator",
            "organization": "Metro Police Department"
        }' | jq '.'
    
    print_step "1.2" "Register Forensic Expert"
    curl -s -X POST $BASE_URL/api/participants \
        -H "Content-Type: application/json" \
        -d '{
            "participant_id": "FOR-001",
            "name": "Dr. Sarah Chen",
            "role": "forensic_expert",
            "organization": "State Forensic Laboratory"
        }' | jq '.'
    
    print_step "1.3" "Register Prosecutor"
    curl -s -X POST $BASE_URL/api/participants \
        -H "Content-Type: application/json" \
        -d '{
            "participant_id": "PRO-001",
            "name": "ADA Robert Williams",
            "role": "prosecutor",
            "organization": "District Attorney Office"
        }' | jq '.'
    
    print_step "1.4" "Register Judge"
    curl -s -X POST $BASE_URL/api/participants \
        -H "Content-Type: application/json" \
        -d '{
            "participant_id": "JUD-001",
            "name": "Judge Patricia Anderson",
            "role": "judge",
            "organization": "District Court"
        }' | jq '.'
    
    print_step "1.5" "List All Participants"
    curl -s -X GET $BASE_URL/api/participants | jq '.'
}

# Test 2: Create Evidence
test_create_evidence() {
    print_header "TEST 2: EVIDENCE CREATION"
    
    # Calculate hash for evidence
    EVIDENCE_HASH=$(echo -n "Crime scene photo evidence file content" | sha256sum | cut -d' ' -f1)
    EVIDENCE_ID=${EVIDENCE_HASH:0:16}
    
    print_step "2.1" "Create Evidence Item"
    echo "Evidence ID: $EVIDENCE_ID"
    echo "File Hash: $EVIDENCE_HASH"
    
    curl -s -X POST $BASE_URL/api/evidence \
        -H "Content-Type: application/json" \
        -d "{
            \"evidence_id\": \"$EVIDENCE_ID\",
            \"description\": \"Crime scene photographs - Main entrance\",
            \"creator_id\": \"INV-001\",
            \"file_hash\": \"$EVIDENCE_HASH\",
            \"file_location\": \"/evidence_store/case_001/photos.zip\",
            \"case_id\": \"CASE-2026-001\",
            \"metadata\": {
                \"type\": \"photograph\",
                \"count\": 25,
                \"resolution\": \"4K\",
                \"timestamp\": \"2026-01-08T10:30:00\"
            }
        }" | jq '.'
    
    # Save for later tests
    echo $EVIDENCE_ID > /tmp/evidence_id.txt
    echo $EVIDENCE_HASH > /tmp/evidence_hash.txt
}

# Test 3: View Evidence
test_view_evidence() {
    print_header "TEST 3: EVIDENCE RETRIEVAL"
    
    EVIDENCE_ID=$(cat /tmp/evidence_id.txt)
    
    print_step "3.1" "Get Specific Evidence"
    curl -s -X GET $BASE_URL/api/evidence/$EVIDENCE_ID | jq '.'
    
    print_step "3.2" "List All Evidence"
    curl -s -X GET $BASE_URL/api/evidence | jq '.'
    
    print_step "3.3" "Get Evidence by Case"
    curl -s -X GET $BASE_URL/api/cases/CASE-2026-001/evidence | jq '.'
}

# Test 4: Transfer Evidence
test_transfer_evidence() {
    print_header "TEST 4: EVIDENCE TRANSFER"
    
    EVIDENCE_ID=$(cat /tmp/evidence_id.txt)
    
    print_step "4.1" "Transfer from Investigator to Forensic Expert"
    curl -s -X POST $BASE_URL/api/evidence/transfer \
        -H "Content-Type: application/json" \
        -d "{
            \"evidence_id\": \"$EVIDENCE_ID\",
            \"from_owner_id\": \"INV-001\",
            \"to_owner_id\": \"FOR-001\",
            \"reason\": \"Transfer to forensic laboratory for analysis\"
        }" | jq '.'
    
    print_step "4.2" "Transfer from Forensic Expert to Prosecutor"
    curl -s -X POST $BASE_URL/api/evidence/transfer \
        -H "Content-Type: application/json" \
        -d "{
            \"evidence_id\": \"$EVIDENCE_ID\",
            \"from_owner_id\": \"FOR-001\",
            \"to_owner_id\": \"PRO-001\",
            \"reason\": \"Analysis complete - Transfer for prosecution\"
        }" | jq '.'
    
    print_step "4.3" "Transfer from Prosecutor to Judge"
    curl -s -X POST $BASE_URL/api/evidence/transfer \
        -H "Content-Type: application/json" \
        -d "{
            \"evidence_id\": \"$EVIDENCE_ID\",
            \"from_owner_id\": \"PRO-001\",
            \"to_owner_id\": \"JUD-001\",
            \"reason\": \"Evidence submitted for court proceedings\"
        }" | jq '.'
}

# Test 5: Evidence History
test_evidence_history() {
    print_header "TEST 5: CHAIN OF CUSTODY HISTORY"
    
    EVIDENCE_ID=$(cat /tmp/evidence_id.txt)
    
    print_step "5.1" "Get Complete Evidence History"
    curl -s -X GET $BASE_URL/api/evidence/$EVIDENCE_ID/history | jq '.'
    
    print_step "5.2" "Get Current Evidence Details"
    curl -s -X GET $BASE_URL/api/evidence/$EVIDENCE_ID | jq '.data.transfer_history'
}

# Test 6: Verify Evidence
test_verify_evidence() {
    print_header "TEST 6: EVIDENCE INTEGRITY VERIFICATION"
    
    EVIDENCE_ID=$(cat /tmp/evidence_id.txt)
    EVIDENCE_HASH=$(cat /tmp/evidence_hash.txt)
    
    print_step "6.1" "Verify with Correct Hash"
    curl -s -X POST $BASE_URL/api/evidence/$EVIDENCE_ID/verify \
        -H "Content-Type: application/json" \
        -d "{
            \"file_hash\": \"$EVIDENCE_HASH\"
        }" | jq '.'
    
    print_step "6.2" "Verify with Incorrect Hash (Tampering Detection)"
    curl -s -X POST $BASE_URL/api/evidence/$EVIDENCE_ID/verify \
        -H "Content-Type: application/json" \
        -d '{
            "file_hash": "0000000000000000000000000000000000000000000000000000000000000000"
        }' | jq '.'
}

# Test 7: Blockchain Operations
test_blockchain() {
    print_header "TEST 7: BLOCKCHAIN VERIFICATION"
    
    print_step "7.1" "Get Blockchain Info"
    curl -s -X GET $BASE_URL/api/blockchain/info | jq '.'
    
    print_step "7.2" "Verify Blockchain Integrity"
    curl -s -X GET $BASE_URL/api/blockchain/verify | jq '.'
    
    print_step "7.3" "Get Full Blockchain"
    curl -s -X GET $BASE_URL/api/blockchain | jq '.data | length' | \
        xargs -I {} echo "Total blocks in blockchain: {}"
}

# Test 8: Utility Functions
test_utilities() {
    print_header "TEST 8: UTILITY FUNCTIONS"
    
    print_step "8.1" "Calculate Hash"
    curl -s -X POST $BASE_URL/api/hash \
        -H "Content-Type: application/json" \
        -d '{
            "content": "Test data for hashing"
        }' | jq '.'
    
    print_step "8.2" "Health Check"
    curl -s -X GET $BASE_URL/api/health | jq '.'
    
    print_step "8.3" "Storage Statistics"
    curl -s -X GET $BASE_URL/api/store/stats | jq '.'
}

# Test 9: Error Handling
test_error_cases() {
    print_header "TEST 9: ERROR HANDLING"
    
    print_step "9.1" "Try to Create Evidence with Non-existent Creator"
    curl -s -X POST $BASE_URL/api/evidence \
        -H "Content-Type: application/json" \
        -d '{
            "evidence_id": "test123",
            "description": "Test",
            "creator_id": "NONEXISTENT",
            "file_hash": "hash123",
            "file_location": "/test",
            "case_id": "TEST"
        }' | jq '.'
    
    print_step "9.2" "Try to Transfer Evidence by Non-owner"
    EVIDENCE_ID=$(cat /tmp/evidence_id.txt)
    curl -s -X POST $BASE_URL/api/evidence/transfer \
        -H "Content-Type: application/json" \
        -d "{
            \"evidence_id\": \"$EVIDENCE_ID\",
            \"from_owner_id\": \"INV-001\",
            \"to_owner_id\": \"FOR-001\",
            \"reason\": \"Unauthorized transfer attempt\"
        }" | jq '.'
    
    print_step "9.3" "Try to Get Non-existent Evidence"
    curl -s -X GET $BASE_URL/api/evidence/nonexistent123 | jq '.'
}

# Test 10: Delete Evidence
test_delete_evidence() {
    print_header "TEST 10: EVIDENCE DELETION"
    
    # Create temporary evidence for deletion
    TEMP_HASH=$(echo -n "Temporary evidence for deletion test" | sha256sum | cut -d' ' -f1)
    TEMP_ID=${TEMP_HASH:0:16}
    
    print_step "10.1" "Create Temporary Evidence"
    curl -s -X POST $BASE_URL/api/evidence \
        -H "Content-Type: application/json" \
        -d "{
            \"evidence_id\": \"$TEMP_ID\",
            \"description\": \"Temporary test evidence\",
            \"creator_id\": \"INV-001\",
            \"file_hash\": \"$TEMP_HASH\",
            \"file_location\": \"/temp/test.dat\",
            \"case_id\": \"TEST-001\"
        }" | jq '.'
    
    print_step "10.2" "Delete Evidence (Soft Delete)"
    curl -s -X DELETE $BASE_URL/api/evidence/$TEMP_ID \
        -H "Content-Type: application/json" \
        -d '{
            "requester_id": "INV-001",
            "reason": "Test deletion - Evidence no longer needed"
        }' | jq '.'
    
    print_step "10.3" "Verify Evidence is Inactive"
    curl -s -X GET $BASE_URL/api/evidence/$TEMP_ID | jq '.data.is_active'
}

# Main execution
main() {
    print_header "FORENSIC-CHAIN API TESTING SUITE"
    echo "This script will test all API endpoints with realistic data"
    echo "Make sure the API server is running: python api/app.py"
    echo ""
    read -p "Press ENTER to continue..."
    
    check_server
    test_participants
    test_create_evidence
    test_view_evidence
    test_transfer_evidence
    test_evidence_history
    test_verify_evidence
    test_blockchain
    test_utilities
    test_error_cases
    test_delete_evidence
    
    print_header "ALL TESTS COMPLETED"
    print_success "API testing suite finished successfully"
    echo ""
    echo "Cleanup: Removing temporary files..."
    rm -f /tmp/evidence_id.txt /tmp/evidence_hash.txt
    print_success "Cleanup complete"
    echo ""
}

# Run main function
main
