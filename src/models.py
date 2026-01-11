"""
Models Module - Forensic Chain
Defines objects: Digital Evidence and Participant.
"""
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ParticipantRole(Enum):
    """Roles of participants in the system."""
    INVESTIGATOR = "investigator"      # Investigator
    FORENSIC_EXPERT = "forensic_expert" # Forensic Expert
    PROSECUTOR = "prosecutor"          # Prosecutor  
    JUDGE = "judge"                    # Judge
    ADMIN = "admin"                    # Administrator


@dataclass
class Participant:
    """Participant in the network."""
    participant_id: str
    name: str
    role: ParticipantRole
    organization: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "participant_id": self.participant_id,
            "name": self.name,
            "role": self.role.value,
            "organization": self.organization,
            "created_at": self.created_at
        }


@dataclass
class TransferRecord:
    """Ownership transfer record."""
    from_owner: str
    to_owner: str
    timestamp: str
    reason: str
    
    def to_dict(self) -> dict:
        return {
            "from_owner": self.from_owner,
            "to_owner": self.to_owner,
            "timestamp": self.timestamp,
            "reason": self.reason
        }


@dataclass
class Evidence:
    """Digital Evidence."""
    evidence_id: str           # ID = SHA256 hash of original content
    description: str           # Evidence description
    creator_id: str            # Creator ID
    current_owner_id: str      # Current owner ID
    file_hash: str             # Hash of original file
    file_location: str         # Storage location of original file
    case_id: str               # Case ID
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True     # Active status
    transfer_history: List[TransferRecord] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "description": self.description,
            "creator_id": self.creator_id,
            "current_owner_id": self.current_owner_id,
            "file_hash": self.file_hash,
            "file_location": self.file_location,
            "case_id": self.case_id,
            "created_at": self.created_at,
            "is_active": self.is_active,
            "transfer_history": [t.to_dict() for t in self.transfer_history],
            "metadata": self.metadata
        }


def generate_evidence_id(file_content: bytes) -> str:
    """Generate evidence ID from file content (SHA256)."""
    return hashlib.sha256(file_content).hexdigest()


def generate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()
