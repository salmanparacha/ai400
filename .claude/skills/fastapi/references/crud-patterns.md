# FastAPI CRUD Patterns

Comprehensive guide to implementing CRUD operations in FastAPI with PostgreSQL.

## Table of Contents

- Database Setup
- Models and Schemas
- CRUD Operations
- Async Patterns
- Error Handling
- Pagination
- Filtering and Sorting

## Database Setup

### SQLAlchemy with AsyncPG

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Create async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5432/dbname",
    echo=True,
    future=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Models and Schemas

### Separating Concerns

Keep SQLAlchemy models and Pydantic schemas separate:

```python
# models.py - Database models
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
```

```python
# schemas.py - Pydantic schemas
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

## CRUD Operations

### Create

```python
@router.post("/users/", response_model=User, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check for existing user
    result = await db.execute(
        select(UserModel).where(UserModel.email == user.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "User already exists")

    # Create new user
    db_user = UserModel(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

### Read (Single)

```python
@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

### Read (Multiple with Pagination)

```python
@router.get("/users/", response_model=list[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserModel).offset(skip).limit(limit)
    )
    return result.scalars().all()
```

### Update

Use PATCH for partial updates:

```python
@router.patch("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user
```

### Delete

```python
@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")

    await db.delete(user)
    await db.commit()
```

## Filtering and Sorting

```python
@router.get("/users/", response_model=list[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    sort_by: str = "id",
    db: AsyncSession = Depends(get_db)
):
    query = select(UserModel)

    # Apply filters
    if search:
        query = query.where(
            (UserModel.username.ilike(f"%{search}%")) |
            (UserModel.email.ilike(f"%{search}%"))
        )

    # Apply sorting
    if hasattr(UserModel, sort_by):
        query = query.order_by(getattr(UserModel, sort_by))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()
```

## Relationships

### One-to-Many

```python
# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")
```

### Loading Related Data

```python
# Eager loading with joinedload
from sqlalchemy.orm import joinedload

result = await db.execute(
    select(UserModel)
    .options(joinedload(UserModel.items))
    .where(UserModel.id == user_id)
)
user = result.unique().scalar_one_or_none()
```

## Error Handling

```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

try:
    db.add(db_user)
    await db.commit()
except IntegrityError:
    await db.rollback()
    raise HTTPException(400, "Duplicate entry")
```

## Transactions

```python
async def transfer_items(
    from_user_id: int,
    to_user_id: int,
    item_ids: list[int],
    db: AsyncSession
):
    async with db.begin():  # Transaction
        # Move items
        result = await db.execute(
            select(ItemModel).where(
                ItemModel.id.in_(item_ids),
                ItemModel.owner_id == from_user_id
            )
        )
        items = result.scalars().all()

        for item in items:
            item.owner_id = to_user_id

        # Commit happens automatically if no exception
```
