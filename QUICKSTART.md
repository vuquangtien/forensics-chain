# 🚀 QUICK START GUIDE

Get started with Forensic-Chain in 5 minutes!

---

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Terminal/Command line

---

## 1️⃣ Installation (2 minutes)

```bash
# Navigate to project directory
cd forensic-chain

# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 2️⃣ Run Tests (1 minute)

```bash
# Verify everything works
python tests/test_system.py
```

**Expected:** All tests pass with ✓ marks

---

## 3️⃣ Run Demo (2 minutes)

```bash
# Watch complete forensic workflow
python demo_complete.py
```

**What you'll see:**
- Participant registration
- Evidence collection
- Chain of custody transfers
- Integrity verification
- Complete audit trail

---

## 4️⃣ Try the API (Optional)

### Terminal 1: Start Server
```bash
python api/app.py
```

### Terminal 2: Test Endpoints
```bash
# Check health
curl http://localhost:5000/api/health | jq

# Run full test suite (requires jq)
./test_api.sh
```

---

## 📚 What's Next?

### Learn More
- Read [README.md](README.md) for complete documentation
- Check [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) for project details

### Use the System
```python
from src.smart_contract import ForensicContract

# Initialize
contract = ForensicContract()

# Register participants
contract.register_participant(
    "INV001", "Detective Smith", 
    "investigator", "Police Dept"
)

# Create evidence
contract.create_evidence(
    evidence_id="abc123",
    description="Crime scene photo",
    creator_id="INV001",
    file_hash="hash_here",
    file_location="/path/to/file",
    case_id="CASE-001"
)

# Transfer evidence
contract.transfer_evidence(
    "abc123", "INV001", "FOR001",
    "Transfer for analysis"
)

# Verify integrity
contract.verify_evidence_integrity("abc123", "hash_here")
```

---

## 🎯 Key Commands

| Command | Purpose |
|---------|---------|
| `python tests/test_system.py` | Run all tests |
| `python demo_complete.py` | Complete demo |
| `python api/app.py` | Start API server |
| `./test_api.sh` | Test all API endpoints |

---

## 💡 Key Features

✅ **4 Main Functions**
- Create Evidence
- Transfer Evidence
- Delete Evidence
- Display Evidence

✅ **Access Control**
- Role-based permissions
- Only authorized users can create evidence
- Ownership tracking

✅ **Blockchain Security**
- Immutable records
- Tamper detection
- Complete audit trail

✅ **Evidence Storage**
- Separate file storage
- Hash verification
- Case organization

---

## 🆘 Troubleshooting

### Tests fail?
```bash
# Make sure you're in virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API won't start?
```bash
# Check if port 5000 is free
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Use different port
# Edit api/app.py, change port=5000 to port=5001
```

### Demo crashes?
```bash
# Run with Python directly
python3 demo_complete.py

# Check Python version
python --version  # Should be 3.8+
```

---

## 📞 Need Help?

1. Check [README.md](README.md) for detailed docs
2. Review [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md)
3. Examine test files in `tests/`
4. Look at demo script `demo_complete.py`

---

**That's it! You're ready to use Forensic-Chain! 🎉**
