"""
Blockchain Core Module - Forensic Chain
This module implements the basic blockchain mechanism for immutable transaction storage.
"""
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class Block:
    """Represents a block in the blockchain."""
    
    def __init__(self, index: int, transactions: List[Dict], previous_hash: str, timestamp: str = None):
        self.index = index
        self.timestamp = timestamp or datetime.now().isoformat()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA256 hash of the block."""
        block_data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_data.encode()).hexdigest()
    
    def mine(self, difficulty: int = 2):
        """Mine block with given difficulty (simple Proof of Work)."""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }


class Blockchain:
    """Manages blockchain and pending transactions."""
    
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = difficulty
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create genesis block (first block)."""
        genesis = Block(0, [{"type": "genesis", "message": "Forensic-Chain Genesis Block"}], "0")
        genesis.mine(self.difficulty)
        self.chain.append(genesis)
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain."""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict) -> str:
        """Add transaction to pending list and return transaction_id."""
        transaction["transaction_id"] = hashlib.sha256(
            json.dumps(transaction, sort_keys=True).encode()
        ).hexdigest()[:16]
        transaction["timestamp"] = datetime.now().isoformat()
        self.pending_transactions.append(transaction)
        return transaction["transaction_id"]
    
    def mine_pending_transactions(self) -> Optional[Block]:
        """Mine new block containing pending transactions."""
        if not self.pending_transactions:
            return None
        
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.get_latest_block().hash
        )
        new_block.mine(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block
    
    def is_chain_valid(self) -> bool:
        """Verify chain integrity."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Verify hash of current block
            if current.hash != current.calculate_hash():
                return False
            
            # Verify link with previous block
            if current.previous_hash != previous.hash:
                return False
        
        return True
    
    def get_transaction_history(self, evidence_id: str) -> List[Dict]:
        """Get complete transaction history of an evidence."""
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("evidence_id") == evidence_id:
                    history.append({**tx, "block_index": block.index, "block_hash": block.hash})
        return history
    
    def to_dict(self) -> List[Dict]:
        """Convert entire blockchain to list of dictionaries."""
        return [block.to_dict() for block in self.chain]
