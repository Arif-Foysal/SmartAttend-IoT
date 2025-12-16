
import sys
import os
sys.path.append(os.getcwd()) # Add valid path

import asyncio
from backend.database import AsyncSessionLocal
from backend.models import Student, StudentImage
from sqlalchemy import select, func

async def check_data():
    async with AsyncSessionLocal() as session:
        # Count students
        result = await session.execute(select(func.count(Student.id)))
        student_count = result.scalar()
        
        # Count images
        result = await session.execute(select(func.count(StudentImage.id)))
        image_count = result.scalar()
        
        print(f"Students: {student_count}")
        print(f"Images: {image_count}")
        
        # List students and their image counts
        result = await session.execute(select(Student))
        students = result.scalars().all()
        for s in students:
            # Re-query to count images for this student if eager load isn't set up in this context
            # Or just check eager load if we used selectinload. 
            # Simpler: just print ID/Name
            print(f"Student: {s.id} - {s.name}")

if __name__ == "__main__":
    asyncio.run(check_data())
