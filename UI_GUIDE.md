# Forensic-Chain Web UI Guide 🎨

## 🚀 Getting Started

### Starting the UI

```bash
cd /home/vqt/forensic-chain
python api/app.py
```

Then open your browser to: **http://localhost:5000**

## 📋 Features Overview

### 1. 📊 Dashboard Tab
- View system statistics (participants, evidence, blocks, chain validity)
- System overview and quick start guide
- Key features explanation

### 2. 👥 Participants Tab
- **Register new participants**: Add investigators, forensic experts, prosecutors, judges
- View all registered participants in a card layout
- Each card shows: ID, name, role, and organization

**Example Workflow:**
1. Fill in the registration form:
   - Participant ID: `INV-001`
   - Full Name: `Detective John Smith`
   - Role: `Investigator`
   - Organization: `Metro Police Department`
2. Click "Register Participant"
3. See the new participant card appear below

### 3. 📁 Evidence Tab
- **Create new evidence**: Record digital evidence with metadata
- View all evidence records
- Click on evidence cards to see full chain of custody details

**Example Workflow:**
1. Fill in the evidence form:
   - Description: `Seized laptop from suspect's residence`
   - Case ID: `CASE-2026-001`
   - Creator: Select an investigator or forensic expert
   - Evidence Type: `Disk Image`
   - File Location: `/evidence_store/case_001/laptop_image.dd`
2. Click "Create Evidence"
3. Evidence is recorded on blockchain with SHA-256 hash

### 4. 🔄 Transfer Tab
- **Transfer evidence custody**: Move evidence between participants
- View transfer workflow timeline
- Ensure proper chain of custody

**Example Workflow:**
1. Enter the evidence ID to transfer
2. Select current owner (from dropdown)
3. Select new owner (to dropdown)
4. Provide transfer reason: `Transferring for forensic analysis`
5. Click "Transfer Evidence"

**Typical Transfer Flow:**
```
Investigator → Forensic Expert → Prosecutor → Judge
```

### 5. ⛓️ Blockchain Tab
- **Visualize the entire blockchain**: See all blocks with their data
- **Verify integrity**: Click "Verify Integrity" to ensure chain hasn't been tampered with
- View block details including:
  - Index
  - Timestamp
  - Previous Hash
  - Current Hash
  - Transaction count
  - Nonce (proof of work)

## 🎯 Complete Demo Scenario

### Step 1: Setup Participants
Register 4 participants (one of each role):

1. **Investigator**
   - ID: `INV-001`
   - Name: `Detective Sarah Johnson`
   - Role: `Investigator`
   - Organization: `City Police Department`

2. **Forensic Expert**
   - ID: `FOR-001`
   - Name: `Dr. Michael Chen`
   - Role: `Forensic Expert`
   - Organization: `State Forensics Lab`

3. **Prosecutor**
   - ID: `PRO-001`
   - Name: `Attorney Lisa Martinez`
   - Role: `Prosecutor`
   - Organization: `District Attorney Office`

4. **Judge**
   - ID: `JUD-001`
   - Name: `Honorable Robert Williams`
   - Role: `Judge`
   - Organization: `Superior Court`

### Step 2: Create Evidence
Create evidence as the investigator:

- **Description**: `Digital photographs of crime scene`
- **Case ID**: `CASE-2026-001`
- **Creator**: `INV-001` (Detective Sarah Johnson)
- **Evidence Type**: `Photograph`
- **File Location**: `/evidence_store/case_001/photos/scene_01.jpg`

### Step 3: Transfer Through Chain of Custody

**Transfer 1**: Investigator → Forensic Expert
- Evidence ID: `EVID-xxx` (copy from evidence card)
- From: `INV-001`
- To: `FOR-001`
- Reason: `Transferring for technical analysis and hash verification`

**Transfer 2**: Forensic Expert → Prosecutor
- From: `FOR-001`
- To: `PRO-001`
- Reason: `Analysis complete, forwarding for case preparation`

**Transfer 3**: Prosecutor → Judge
- From: `PRO-001`
- To: `JUD-001`
- Reason: `Submitting evidence for trial proceedings`

### Step 4: View Chain of Custody
1. Go to **Evidence Tab**
2. Click on the evidence card
3. Modal shows complete chain of custody:
   - All transfers
   - Timestamps
   - Participants involved
   - Transfer reasons
   - Cryptographic hashes at each step

### Step 5: Verify Blockchain Integrity
1. Go to **Blockchain Tab**
2. Click "Verify Integrity" button
3. System validates:
   - All hashes are correct
   - Chain is unbroken
   - No tampering detected
4. Green checkmark confirms integrity ✅

## 🎨 UI Features

### Modern Design
- Clean, professional interface
- Responsive layout (works on all screen sizes)
- Color-coded sections for easy navigation
- Smooth animations and transitions

### Real-Time Updates
- Dashboard statistics update automatically
- New evidence appears immediately
- Blockchain visualizes in real-time

### Interactive Elements
- Modal dialogs for detailed views
- Form validation
- Dropdown menus for easy selection
- Hover effects for better UX

### Visual Feedback
- Success messages (green)
- Error messages (red)
- Loading states
- Confirmation dialogs

## 🔒 Security Features Demonstrated

1. **Immutability**: Once created, evidence records cannot be modified
2. **Traceability**: Complete chain of custody visible for all evidence
3. **Access Control**: Only authorized roles can perform certain actions
4. **Cryptographic Hashing**: All files verified with SHA-256
5. **Proof of Work**: Each block mined to prevent tampering
6. **Chain Validation**: Automatic detection of any unauthorized changes

## 💡 Tips for Demo

1. **Open multiple browser tabs** to simulate different users
2. **Use realistic data** (names, case numbers, descriptions)
3. **Show the blockchain visualization** after each action
4. **Verify integrity frequently** to demonstrate security
5. **Click on evidence cards** to show detailed chain of custody
6. **Explain each step** as you perform actions

## 🎓 Key Points to Highlight

### For Technical Audience:
- SHA-256 cryptographic hashing
- Proof of Work mining algorithm
- Immutable blockchain structure
- RESTful API architecture
- Role-based access control

### For Legal Audience:
- Maintains complete chain of custody
- Provides admissible evidence trail
- Prevents evidence tampering
- Documents all handling procedures
- Meets legal requirements for evidence integrity

### For Management:
- Reduces evidence handling errors
- Improves case management efficiency
- Provides audit trail for compliance
- Increases trust in evidence handling
- Modernizes forensic procedures

## 🛠️ Troubleshooting

**If UI doesn't load:**
```bash
# Check if server is running
curl http://localhost:5000/api/health

# Restart server
pkill -f "python api/app.py"
python api/app.py
```

**If you get API errors:**
- Check that participants exist before creating evidence
- Ensure evidence exists before transferring
- Verify participant IDs are correct

## 📞 Support

For issues or questions, check:
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick setup guide
- `tests/test_system.py` - Example usage

---

**Built with:** Python, Flask, Blockchain Technology, SHA-256, Proof of Work

**For:** Digital Forensics Chain of Custody Management
