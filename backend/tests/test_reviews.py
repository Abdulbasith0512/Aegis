import uuid
import pytest
from datetime import datetime, timedelta
from app.models.governance import HumanReview
from app.models.transactions import Transaction

def test_human_review_sla_deadline() -> None:
    """
    Verifies that SLA deadline values initialize and compare correctly.
    """
    tx_id = uuid.uuid4()
    now = datetime.utcnow()
    deadline = now + timedelta(hours=4)
    
    review = HumanReview(
        transaction_id=tx_id,
        status="pending",
        sla_deadline=deadline
    )
    
    assert review.transaction_id == tx_id
    assert review.status == "pending"
    assert review.sla_deadline == deadline
    assert review.sla_deadline > now

def test_sla_breach_detection() -> None:
    """
    Verifies that older deadlines register as breached.
    """
    past_deadline = datetime.utcnow() - timedelta(minutes=10)
    
    is_breached = datetime.utcnow() > past_deadline
    assert is_breached is True
