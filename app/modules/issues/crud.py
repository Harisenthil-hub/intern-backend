"""
CRUD operations for Gas Issue to Filling.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.issues.models import GasIssue, IssueStatus
from app.modules.procurement.models import InventoryTransaction, InventoryType, ReferenceType
from app.modules.issues.schemas import IssueCreate, IssueUpdate
from app.modules.tanks.models import Tank


def _next_issue_code(db: Session) -> str:
    last = db.query(GasIssue.issue_code).order_by(GasIssue.issue_code.desc()).first()
    if last is None:
        return "IS-001"

    try:
        number = int(last[0].split("-")[1]) + 1
    except (IndexError, ValueError):
        number = 1
    return f"IS-{number:03d}"


def _validate_frontend_rules(
    *,
    db: Session,
    tank_id: str,
    gas_type: str,
    quantity_issued: float,
) -> Tank:
    tank = db.query(Tank).filter(Tank.tank_id == tank_id).first()
    if not tank:
        raise ValueError("Tank not found")

    if tank.gas_type != gas_type:
        raise ValueError("Selected tank does not match gas type")

    current_level = tank.current_level or 0.0
    if quantity_issued > current_level:
        raise ValueError("Insufficient gas in tank")

    return tank


def _post_issue_atomic(db: Session, issue: GasIssue) -> GasIssue:
    if issue.status == IssueStatus.posted.value:
        raise ValueError("Already posted")

    tank = db.query(Tank).filter(Tank.tank_id == issue.tank_id).first()
    if not tank:
        raise ValueError("Tank not found")

    if tank.gas_type != issue.gas_type:
        raise ValueError("Selected tank does not match gas type")

    if issue.quantity_issued > (tank.current_level or 0.0):
        raise ValueError("Insufficient gas in tank")

    try:
        locked_tank = (
            db.query(Tank)
            .filter(Tank.tank_id == issue.tank_id)
            .with_for_update()
            .first()
        )
        if not locked_tank:
            raise ValueError("Tank not found")

        if locked_tank.gas_type != issue.gas_type:
            raise ValueError("Selected tank does not match gas type")

        current_level = locked_tank.current_level or 0.0
        if issue.quantity_issued > current_level:
            raise ValueError("Insufficient gas in tank")

        locked_tank.current_level = current_level - issue.quantity_issued

        inventory_transaction = InventoryTransaction(
            tank_id=issue.tank_id,
            type=InventoryType.outgoing.value,
            reference_type=ReferenceType.issue.value,
            reference_id=issue.id,
            quantity=issue.quantity_issued,
        )
        db.add(inventory_transaction)

        issue.status = IssueStatus.posted.value

        db.commit()
        db.refresh(issue)
        return issue
    except Exception:
        db.rollback()
        raise


def create_issue(db: Session, payload: IssueCreate) -> GasIssue:
    _validate_frontend_rules(
        db=db,
        tank_id=payload.tank_id,
        gas_type=payload.gas_type,
        quantity_issued=payload.quantity_issued,
    )

    should_post = payload.status == IssueStatus.posted.value

    issue = GasIssue(
        issue_code=_next_issue_code(db),
        tank_id=payload.tank_id,
        gas_type=payload.gas_type,
        date=payload.date,
        quantity_issued=payload.quantity_issued,
        filling_batch_id=payload.filling_batch_id,
        status=IssueStatus.draft.value,
    )

    db.add(issue)
    if should_post:
        db.flush()
        return _post_issue_atomic(db, issue)

    db.commit()
    db.refresh(issue)
    return issue


def get_all_issues(db: Session) -> list[GasIssue]:
    return db.query(GasIssue).order_by(GasIssue.issue_code.desc()).all()


def get_issue_by_code(db: Session, issue_code: str) -> GasIssue | None:
    return db.query(GasIssue).filter(GasIssue.issue_code == issue_code).first()


def update_issue(db: Session, issue: GasIssue, payload: IssueUpdate) -> GasIssue:
    requested_status = payload.status if payload.status is not None else issue.status
    update_data = payload.model_dump(exclude_unset=True, by_alias=False)

    if issue.status == IssueStatus.posted.value:
        if set(update_data.keys()) == {"status"} and requested_status == IssueStatus.posted.value:
            raise ValueError("Already posted")
        raise ValueError("Posted records cannot be edited")

    for field, value in update_data.items():
        if field == "status":
            continue
        setattr(issue, field, value)

    _validate_frontend_rules(
        db=db,
        tank_id=issue.tank_id,
        gas_type=issue.gas_type,
        quantity_issued=issue.quantity_issued,
    )

    if requested_status == IssueStatus.posted.value:
        return _post_issue_atomic(db, issue)

    db.commit()
    db.refresh(issue)
    return issue
