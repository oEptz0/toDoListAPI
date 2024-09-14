from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    db_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
        deadline=task.deadline,
        owner_id=user_id,
        category_id=task.category_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    completed: bool | None = None,
    category_id: int | None = None,
    search: str | None = None
):
    query = db.query(models.Task).filter(models.Task.owner_id == user_id)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    if category_id is not None:
        query = query.filter(models.Task.category_id == category_id)
    if search:
        query = query.filter(models.Task.title.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()



def get_task(db: Session, task_id: int, user_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == user_id).first()

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate, user_id: int):
    update_data = task.model_dump(exclude_unset=True)
    result = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user_id
    ).update(update_data, synchronize_session='fetch')
    
    if not result:
        return None
    
    db.commit()
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    return db_task

def delete_task(db: Session, task_id: int, user_id: int):
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None
    db.delete(db_task)
    db.commit()
    return db_task

def get_category_by_name(db: Session, user_id: int, name: str):
    return db.query(models.Category).filter(
        models.Category.owner_id == user_id,
        models.Category.name == name
    ).first()

def get_category(db: Session, user_id: int, category_id: int):
    return db.query(models.Category).filter(
        models.Category.owner_id == user_id,
        models.Category.id == category_id
    ).first()

def get_categories(db: Session, user_id: int):
    return db.query(models.Category).filter(
        models.Category.owner_id == user_id
    ).all()

def create_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(
        name=category.name,
        owner_id=user_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, user_id: int, category_id: int):
    db_category = get_category(db, user_id, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category
