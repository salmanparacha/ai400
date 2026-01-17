"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None
    is_active: bool | None = None


class User(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# Item Schemas
class ItemBase(BaseModel):
    """Base item schema."""
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    """Schema for creating an item."""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating an item."""
    title: str | None = None
    description: str | None = None


class Item(ItemBase):
    """Schema for item response."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
