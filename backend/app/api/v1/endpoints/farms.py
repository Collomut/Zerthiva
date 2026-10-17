"""
Farm Management CRUD Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut

router = APIRouter()


@router.get("/", response_model=List[FarmOut])
async def list_farms(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all registered farms"""
    stmt = select(Farm).offset(skip).limit(limit).order_by(Farm.id.asc())
    result = await db.execute(stmt)
    farms = result.scalars().all()
    return farms


@router.post("/", response_model=FarmOut, status_code=status.HTTP_201_CREATED)
async def create_farm(payload: FarmCreate, db: AsyncSession = Depends(get_db)):
    """Register a new pilot farm"""
    farm = Farm(**payload.model_dump())
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
    return farm


@router.get("/{farm_id}", response_model=FarmOut)
async def get_farm(farm_id: int, db: AsyncSession = Depends(get_db)):
    """Get single farm details"""
    stmt = select(Farm).where(Farm.id == farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")
    return farm


@router.put("/{farm_id}", response_model=FarmOut)
async def update_farm(farm_id: int, payload: FarmUpdate, db: AsyncSession = Depends(get_db)):
    """Update farm parameters"""
    stmt = select(Farm).where(Farm.id == farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)

    await db.commit()
    await db.refresh(farm)
    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(farm_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a farm"""
    stmt = select(Farm).where(Farm.id == farm_id)
    result = await db.execute(stmt)
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found")

    await db.delete(farm)
    await db.commit()
    return None
