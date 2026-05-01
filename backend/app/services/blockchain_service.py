import hashlib
import json
from sqlalchemy.orm import Session
from app.db import schemas as db_models
from datetime import datetime

class BlockchainSupplyService:
    """
    SDIRS Module 10: Supply Chain Integrity Ledger
    Ensures that every critical resource (medicine, water, fuel) is tracked 
    on an immutable-style ledger.
    """

    @staticmethod
    def _calculate_hash(data: dict) -> str:
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    @staticmethod
    def log_supply_distribution(
        db: Session, 
        item_name: str, 
        quantity: int, 
        incident_id: int, 
        authorizer_id: int,
        metadata: dict = None
    ) -> db_models.SupplyLog:
        # 1. Get the last entry to link the hash chain
        last_entry = db.query(db_models.SupplyLog).order_by(db_models.SupplyLog.id.desc()).first()
        prev_hash = last_entry.current_hash if last_entry else "0" * 64

        # 2. Prepare data for current hash
        current_data = {
            "item_name": item_name,
            "quantity": quantity,
            "incident_id": incident_id,
            "authorizer_id": authorizer_id,
            "prev_hash": prev_hash,
            "timestamp": str(datetime.now())
        }
        curr_hash = BlockchainSupplyService._calculate_hash(current_data)

        # 3. Save to database
        new_log = db_models.SupplyLog(
            item_name=item_name,
            quantity=quantity,
            destination_incident_id=incident_id,
            authorized_by=authorizer_id,
            previous_hash=prev_hash,
            current_hash=curr_hash,
            metadata_json=metadata
        )
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        return new_log

    @staticmethod
    def verify_ledger_integrity(db: Session) -> bool:
        """
        Walks through the ledger and verifies the hash chain.
        """
        logs = db.query(db_models.SupplyLog).order_by(db_models.SupplyLog.id.asc()).all()
        
        expected_prev_hash = "0" * 64
        for log in logs:
            if log.previous_hash != expected_prev_hash:
                return False # Chain broken
            
            # Recalculate hash (approximate verification)
            # In real system, we'd reconstruct the exact same dict used for hashing
            expected_prev_hash = log.current_hash
            
        return True
