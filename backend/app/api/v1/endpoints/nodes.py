"""
Edge Node Registry & Management Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.node import Node
from app.schemas.node import NodeCreate, NodeOut

router = APIRouter()


@router.get("/", response_model=List[NodeOut])
async def list_nodes(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all deployed edge nodes"""
    stmt = select(Node).offset(skip).limit(limit).order_by(Node.id.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=NodeOut, status_code=status.HTTP_201_CREATED)
async def register_node(payload: NodeCreate, db: AsyncSession = Depends(get_db)):
    """Register an edge node"""
    stmt = select(Node).where(Node.device_id == payload.device_id)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device ID already registered")

    node = Node(**payload.model_dump())
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node


@router.get("/{device_id}", response_model=NodeOut)
async def get_node(device_id: str, db: AsyncSession = Depends(get_db)):
    """Query single node status"""
    stmt = select(Node).where(Node.device_id == device_id)
    res = await db.execute(stmt)
    node = res.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return node


@router.put("/{device_id}/assign/{farm_id}", response_model=NodeOut)
async def assign_node_to_farm(device_id: str, farm_id: int, db: AsyncSession = Depends(get_db)):
    """Links an edge node to a specific farm"""
    stmt = select(Node).where(Node.device_id == device_id)
    res = await db.execute(stmt)
    node = res.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    node.farm_id = farm_id
    await db.commit()
    await db.refresh(node)
    return node
