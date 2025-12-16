from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import pickle
import cv2
import numpy as np
import face_recognition

from fastapi.middleware.cors import CORSMiddleware
import models, schemas, database

app = FastAPI(title="SmartAttend IoT Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await database.init_db()

@app.get("/")
def read_root():
    return {"message": "SmartAttend API is running"}


@app.post("/students/", response_model=schemas.Student)
async def create_student(
    name: str = Form(...),
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(database.get_db)
):
    # Process initial photo
    contents = await photo.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_image)
    if not encodings:
        raise HTTPException(status_code=400, detail="No face found in the photo")
        
    pickled_encoding = pickle.dumps(encodings[0])
    
    # Create student
    new_student = models.Student(name=name)
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    
    # Create image record
    new_image = models.StudentImage(
        student_id=new_student.id,
        encoding=pickled_encoding,
        image=contents # Store actual image data
    )
    db.add(new_image)
    await db.commit()
    
    # Reload with images
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(models.Student)
        .options(selectinload(models.Student.images))
        .where(models.Student.id == new_student.id)
    )
    return result.scalar_one()

@app.get("/students/", response_model=List[schemas.Student])
async def read_students(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(models.Student)
        .options(selectinload(models.Student.images))
        .offset(skip)
        .limit(limit)
    )
    students = result.scalars().all()
    return students

@app.get("/students/sync", response_model=List[schemas.StudentSync])
async def sync_students(db: AsyncSession = Depends(database.get_db)):
    # Return flattened list of all encodings
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(models.Student)
        .options(selectinload(models.Student.images))
    )
    students = result.scalars().all()
    
    sync_data = []
    for student in students:
        for img in student.images:
            if img.encoding:
                 sync_data.append({
                    "id": student.id,
                    "name": student.name,
                    "encoding": img.encoding # Pass raw bytes, schema handles base64
                })
                
    return sync_data

@app.post("/students/{student_id}/images", response_model=schemas.StudentImage)
async def add_student_image(
    student_id: int,
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(database.get_db)
):
    # Verify student exists
    result = await db.execute(select(models.Student).where(models.Student.id == student_id))
    if not result.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Student not found")

    contents = await photo.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_image)
    if not encodings:
        raise HTTPException(status_code=400, detail="No face found in the photo")
        
    pickled_encoding = pickle.dumps(encodings[0])
    
    new_image = models.StudentImage(
        student_id=student_id,
        encoding=pickled_encoding,
        image=contents # Store actual image data
    )
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    return new_image

# ... (delete_student_image and get_student_image remain same)

@app.delete("/students/{student_id}")
async def delete_student(student_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Student).where(models.Student.id == student_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
        
    await db.delete(student)
    await db.commit()
    return {"message": "Student deleted successfully"}

@app.get("/images/{image_id}")
async def get_student_image(image_id: int, db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.StudentImage).where(models.StudentImage.id == image_id))
    img = result.scalar_one_or_none()
    if img is None or img.image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    from fastapi.responses import Response
    return Response(content=img.image, media_type="image/jpeg")

@app.put("/students/{student_id}", response_model=schemas.Student)
async def update_student(
    student_id: int,
    name: str = Form(None),
    db: AsyncSession = Depends(database.get_db)
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(models.Student)
        .options(selectinload(models.Student.images))
        .where(models.Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
        
    if name:
        student.name = name
        await db.commit()
        await db.refresh(student)
        
    return student

# --- Attendance ---

@app.post("/attendance/", response_model=schemas.Attendance)
async def log_attendance(attendance: schemas.AttendanceCreate, db: AsyncSession = Depends(database.get_db)):
    db_attendance = models.Attendance(**attendance.dict())
    if db_attendance.timestamp is None:
        db_attendance.timestamp = datetime.utcnow()
        
    db.add(db_attendance)
    # Remove duplicate add
    await db.commit()
    # Eager load the relationship to avoid MissingGreenlet error during serialization
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(models.Attendance)
        .options(selectinload(models.Attendance.student))
        .where(models.Attendance.id == db_attendance.id)
    )
    db_attendance = result.scalar_one()
    return db_attendance

@app.get("/attendance/", response_model=List[schemas.Attendance])
async def read_attendance(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(database.get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(models.Attendance)
        .options(selectinload(models.Attendance.student))
        .order_by(desc(models.Attendance.timestamp))
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()
    return items
