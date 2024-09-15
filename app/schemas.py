from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    tasks: List['Task'] = []

    class Config:
        from_attributes = True
        
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    deadline: datetime | None = None
    category_id: int | None = None  

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    deadline: datetime | None = None
    category_id: int | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    deadline: datetime | None = None
    category_id: int | None = None
class Task(TaskBase):
    id: int
    owner_id: int
    category: Category | None = None  
    reminder_time: datetime | None = None  
    reminder_sent: bool = False

    class Config:
        from_attributes = True

class ReminderTime(BaseModel):
    reminder_time: datetime