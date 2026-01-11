"""
Evidence Store Module - Forensic Chain
Handles distributed storage of actual evidence files separately from blockchain.
This simulates a secure evidence repository where files are stored with encryption.
"""
import hashlib
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


class EvidenceStore:
    """
    Distributed Evidence Store - manages physical file storage.
    Files are stored separately from blockchain metadata.
    """
    
    def __init__(self, base_path: str = "./evidence_store"):
        """
        Initialize evidence store.
        
        Args:
            base_path: Base directory for storing evidence files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        (self.base_path / "active").mkdir(exist_ok=True)
        (self.base_path / "archived").mkdir(exist_ok=True)
        (self.base_path / "temp").mkdir(exist_ok=True)
    
    def store_evidence(self, file_path: str, evidence_id: str, 
                      case_id: str) -> Tuple[bool, str, str]:
        """
        Store evidence file in secure repository.
        
        Args:
            file_path: Path to original evidence file
            evidence_id: Unique evidence identifier
            case_id: Related case ID
        
        Returns:
            Tuple[bool, str, str]: (Success?, Storage path, File hash)
        """
        try:
            # Verify file exists
            if not os.path.exists(file_path):
                return False, "", f"Source file not found: {file_path}"
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Create case directory
            case_dir = self.base_path / "active" / case_id
            case_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate storage filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = Path(file_path).suffix
            storage_filename = f"{evidence_id}_{timestamp}{file_ext}"
            storage_path = case_dir / storage_filename
            
            # Copy file to storage
            shutil.copy2(file_path, storage_path)
            
            # Create metadata file
            self._create_metadata(storage_path, evidence_id, case_id, file_hash)
            
            return True, str(storage_path), file_hash
            
        except Exception as e:
            return False, "", f"Error storing evidence: {str(e)}"
    
    def retrieve_evidence(self, storage_path: str) -> Tuple[bool, bytes, str]:
        """
        Retrieve evidence file from storage.
        
        Args:
            storage_path: Path to stored evidence
        
        Returns:
            Tuple[bool, bytes, str]: (Success?, File content, Message)
        """
        try:
            if not os.path.exists(storage_path):
                return False, b"", "Evidence file not found in storage"
            
            with open(storage_path, 'rb') as f:
                content = f.read()
            
            return True, content, "Evidence retrieved successfully"
            
        except Exception as e:
            return False, b"", f"Error retrieving evidence: {str(e)}"
    
    def verify_file_integrity(self, storage_path: str, 
                            expected_hash: str) -> Tuple[bool, str]:
        """
        Verify file integrity by comparing hash.
        
        Args:
            storage_path: Path to stored evidence
            expected_hash: Expected hash from blockchain
        
        Returns:
            Tuple[bool, str]: (Valid?, Message)
        """
        try:
            if not os.path.exists(storage_path):
                return False, "File not found in storage"
            
            actual_hash = self._calculate_file_hash(storage_path)
            
            if actual_hash == expected_hash:
                return True, "✓ File integrity verified - No tampering detected"
            else:
                return False, "✗ WARNING: File has been modified! Hash mismatch"
                
        except Exception as e:
            return False, f"Error verifying integrity: {str(e)}"
    
    def archive_evidence(self, storage_path: str, 
                        evidence_id: str) -> Tuple[bool, str]:
        """
        Move evidence to archive (for closed cases).
        
        Args:
            storage_path: Current storage path
            evidence_id: Evidence ID
        
        Returns:
            Tuple[bool, str]: (Success?, New archive path)
        """
        try:
            if not os.path.exists(storage_path):
                return False, "Evidence file not found"
            
            # Create archive path
            filename = Path(storage_path).name
            archive_path = self.base_path / "archived" / filename
            
            # Move file to archive
            shutil.move(storage_path, archive_path)
            
            # Move metadata
            meta_source = Path(storage_path).with_suffix('.meta')
            if meta_source.exists():
                meta_dest = archive_path.with_suffix('.meta')
                shutil.move(meta_source, meta_dest)
            
            return True, str(archive_path)
            
        except Exception as e:
            return False, f"Error archiving evidence: {str(e)}"
    
    def delete_evidence_file(self, storage_path: str) -> Tuple[bool, str]:
        """
        Permanently delete evidence file (use with caution).
        Note: This should only be used with proper authorization.
        
        Args:
            storage_path: Path to evidence file
        
        Returns:
            Tuple[bool, str]: (Success?, Message)
        """
        try:
            if not os.path.exists(storage_path):
                return False, "Evidence file not found"
            
            # Delete file
            os.remove(storage_path)
            
            # Delete metadata
            meta_path = Path(storage_path).with_suffix('.meta')
            if meta_path.exists():
                os.remove(meta_path)
            
            return True, "Evidence file permanently deleted"
            
        except Exception as e:
            return False, f"Error deleting evidence: {str(e)}"
    
    def list_evidence_by_case(self, case_id: str) -> list:
        """
        List all evidence files for a case.
        
        Args:
            case_id: Case ID
        
        Returns:
            List of evidence files
        """
        case_dir = self.base_path / "active" / case_id
        if not case_dir.exists():
            return []
        
        evidence_files = []
        for file_path in case_dir.glob("*"):
            if file_path.suffix != '.meta':
                evidence_files.append({
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat()
                })
        
        return evidence_files
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _create_metadata(self, storage_path: Path, evidence_id: str,
                        case_id: str, file_hash: str):
        """Create metadata file for evidence."""
        metadata = {
            "evidence_id": evidence_id,
            "case_id": case_id,
            "file_hash": file_hash,
            "stored_at": datetime.now().isoformat(),
            "file_size": storage_path.stat().st_size,
            "original_filename": storage_path.name
        }
        
        meta_path = storage_path.with_suffix('.meta')
        with open(meta_path, 'w') as f:
            import json
            json.dump(metadata, f, indent=2)
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics."""
        active_count = len(list((self.base_path / "active").rglob("*.*")))
        archived_count = len(list((self.base_path / "archived").rglob("*.*")))
        
        # Calculate total size
        total_size = sum(
            f.stat().st_size 
            for f in self.base_path.rglob("*") 
            if f.is_file() and f.suffix != '.meta'
        )
        
        return {
            "active_evidence": active_count // 2,  # Divide by 2 (file + meta)
            "archived_evidence": archived_count // 2,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "base_path": str(self.base_path)
        }
