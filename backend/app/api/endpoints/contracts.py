from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timedelta, timezone

from app.api import deps
from app.models.user import User
from app.models.contract import Contract
from app.models.wallet import Wallet
from app.models.inventory import Inventory
from app.models.fleet import Fleet
from app.models.item import Item
from app.schemas.contract import ContractCreate, ContractResponse

router = APIRouter()

@router.post("/", response_model=ContractResponse)
async def create_contract(
    contract_in: ContractCreate,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    # Check Wallet for Reward
    wallet = await db.scalar(select(Wallet).where(Wallet.user_id == current_user.id))
    if not wallet or wallet.balance < contract_in.reward_amount:
        raise HTTPException(status_code=400, detail="Insufficient funds for reward")

    # Check Inventory for Items
    inventory = await db.scalar(
        select(Inventory).where(
            Inventory.planet_id == contract_in.origin_planet_id,
            Inventory.item_id == contract_in.item_id
        )
    )
    if not inventory or inventory.quantity < contract_in.quantity:
        raise HTTPException(status_code=400, detail="Insufficient items at origin")

    # Deduct
    wallet.balance -= contract_in.reward_amount
    inventory.quantity -= contract_in.quantity

    # Create Contract
    contract = Contract(
        issuer_id=current_user.id,
        origin_planet_id=contract_in.origin_planet_id,
        destination_planet_id=contract_in.destination_planet_id,
        item_id=contract_in.item_id,
        quantity=contract_in.quantity,
        reward_amount=contract_in.reward_amount,
        collateral_amount=contract_in.collateral_amount,
        duration_seconds=contract_in.duration_seconds,
        status="OPEN"
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract

@router.get("/", response_model=List[ContractResponse])
async def read_contracts(
    skip: int = 0,
    limit: int = 100,
    status: str = "OPEN",
    db: AsyncSession = Depends(deps.get_db)
):
    # Allow filtering by status
    result = await db.execute(
        select(Contract).where(Contract.status == status).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.post("/{id}/accept", response_model=ContractResponse)
async def accept_contract(
    id: int,
    fleet_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    contract = await db.get(Contract, id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.status != "OPEN":
        raise HTTPException(status_code=400, detail="Contract is not open")
    if contract.issuer_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot accept own contract")

    # Check Collateral
    wallet = await db.scalar(select(Wallet).where(Wallet.user_id == current_user.id))
    if not wallet or wallet.balance < contract.collateral_amount:
        raise HTTPException(status_code=400, detail="Insufficient funds for collateral")

    # Check Fleet
    fleet = await db.get(Fleet, fleet_id)
    if not fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    if fleet.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not fleet owner")
    if fleet.location_planet_id != contract.origin_planet_id:
        raise HTTPException(status_code=400, detail="Fleet not at origin planet")

    # Check Fleet Capacity
    item = await db.get(Item, contract.item_id)
    total_volume = item.volume * contract.quantity

    if total_volume > fleet.cargo_capacity:
         raise HTTPException(status_code=400, detail="Fleet capacity insufficient")

    # Execute Acceptance
    wallet.balance -= contract.collateral_amount

    # Add to Fleet Inventory
    fleet_inv = await db.scalar(
        select(Inventory).where(Inventory.fleet_id == fleet.id, Inventory.item_id == contract.item_id)
    )
    if fleet_inv:
        fleet_inv.quantity += contract.quantity
    else:
        new_inv = Inventory(fleet_id=fleet.id, item_id=contract.item_id, quantity=contract.quantity)
        db.add(new_inv)

    contract.contractor_id = current_user.id
    contract.accepted_at = datetime.now(timezone.utc)
    contract.deadline = datetime.now(timezone.utc) + timedelta(seconds=contract.duration_seconds)
    contract.status = "IN_PROGRESS"

    await db.commit()
    await db.refresh(contract)
    return contract

@router.post("/{id}/complete", response_model=ContractResponse)
async def complete_contract(
    id: int,
    fleet_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db)
):
    contract = await db.get(Contract, id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    if contract.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="Contract not in progress")
    if contract.contractor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check Deadline
    now = datetime.now(timezone.utc)
    deadline = contract.deadline
    if deadline and deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    if deadline and now > deadline:
        contract.status = "FAILED"
        # Collateral logic (Give to Issuer)
        issuer_wallet = await db.scalar(select(Wallet).where(Wallet.user_id == contract.issuer_id))
        if issuer_wallet:
            issuer_wallet.balance += contract.collateral_amount
            # Also return the reward to issuer
            issuer_wallet.balance += contract.reward_amount

        await db.commit()
        await db.refresh(contract)
        raise HTTPException(status_code=400, detail="Contract expired and failed")

    # Check Fleet
    fleet = await db.get(Fleet, fleet_id)
    if not fleet:
        raise HTTPException(status_code=404, detail="Fleet not found")
    if fleet.location_planet_id != contract.destination_planet_id:
        raise HTTPException(status_code=400, detail="Fleet not at destination")

    # Check Items in Fleet
    fleet_inv = await db.scalar(
        select(Inventory).where(Inventory.fleet_id == fleet.id, Inventory.item_id == contract.item_id)
    )
    if not fleet_inv or fleet_inv.quantity < contract.quantity:
        raise HTTPException(status_code=400, detail="Items missing from fleet")

    # Execute Completion
    # 1. Remove from Fleet
    fleet_inv.quantity -= contract.quantity
    if fleet_inv.quantity == 0:
        await db.delete(fleet_inv)

    # 2. Add to Issuer Inventory at Destination
    dest_inv = await db.scalar(
        select(Inventory).where(
            Inventory.planet_id == contract.destination_planet_id,
            Inventory.item_id == contract.item_id
        )
    )

    if dest_inv:
        dest_inv.quantity += contract.quantity
    else:
        dest_inv = Inventory(planet_id=contract.destination_planet_id, item_id=contract.item_id, quantity=contract.quantity)
        db.add(dest_inv)

    # 3. Payout
    contractor_wallet = await db.scalar(select(Wallet).where(Wallet.user_id == current_user.id))
    contractor_wallet.balance += contract.reward_amount
    contractor_wallet.balance += contract.collateral_amount

    contract.status = "COMPLETED"

    await db.commit()
    await db.refresh(contract)
    return contract
