from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta, datetime
from . import crud, schemas, auth, models
from .database import get_db, init_db
from .auth import get_current_user
from app.email_utils import send_email
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

def check_reminders():
    db = next(get_db())  
    tasks = db.query(models.Task).filter(
        models.Task.reminder_time <= datetime.now(),
        models.Task.reminder_sent == False,
        models.Task.completed == False
    ).all()

    for task in tasks:
        try:
            send_email(
                to_email=task.owner.email,
                subject=f"Reminder: {task.title}",
                content=f"This is a reminder for your task: {task.title}. Deadline: {task.deadline}"
            )
            task.reminder_sent = True  
        except Exception as e:
            print(f"Error sending email for task {task.id}: {e}")
    
    db.commit() 


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    scheduler = BackgroundScheduler()
    scheduler.start()

    scheduler.add_job(
        check_reminders,
        trigger=IntervalTrigger(seconds=60)
    )

    yield

    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.post("/tasks/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if task.category_id:
        category = crud.get_category(db, user_id=current_user.id, category_id=task.category_id)
        if category is None:
            raise HTTPException(status_code=400, detail="Invalid category")
    return crud.create_task(db=db, task=task, user_id=current_user.id)

@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    completed: bool | None = Query(None),
    category_id: int | None = Query(None),
    search: str | None = Query(None),
    has_reminder: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    return crud.get_tasks(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        completed=completed,
        category_id=category_id,
        search=search,
        has_reminder=has_reminder
    )

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_task = crud.get_task(db=db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if task.category_id:
        category = crud.get_category(db, user_id=current_user.id, category_id=task.category_id)
        if category is None:
            raise HTTPException(status_code=400, detail="Invalid category")
    db_task = crud.update_task(db=db, task_id=task_id, task=task, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    return db_task

@app.delete("/tasks/{task_id}", response_model=schemas.Task)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    db_task = crud.delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    return db_task

@app.post("/categories/", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_category = crud.get_category_by_name(db, user_id=current_user.id, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="Category already exists")
    return crud.create_category(db=db, category=category, user_id=current_user.id)

@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    categories = crud.get_categories(db=db, user_id=current_user.id)
    return categories

@app.delete("/categories/{category_id}", response_model=schemas.Category)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    db_category = crud.get_category(db=db, user_id=current_user.id, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return crud.delete_category(db=db, user_id=current_user.id, category_id=category_id)
      
@app.put("/tasks/{task_id}/set_reminder", response_model=schemas.Task)
def set_reminder(task_id: int, reminder: schemas.ReminderTime, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id, models.Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.reminder_time = reminder.reminder_time
    task.reminder_sent = False
    db.commit()
    db.refresh(task)
    
    return task
