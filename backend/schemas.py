import base64
from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import List, Optional

class AttendanceBase(BaseModel):
    student_id: int
    timestamp: Optional[datetime] = None
    device_id: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    student: Optional['StudentBase'] = None
    
    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str

class StudentImageBase(BaseModel):
    pass

class StudentImage(StudentImageBase):
    id: int
    student_id: int
    created_at: datetime
    # Encoding not returned by default
    
    class Config:
        from_attributes = True

class Student(StudentBase):
    id: int
    created_at: datetime
    images: List[StudentImage] = []
    
    class Config:
        from_attributes = True

class StudentSync(BaseModel):
    # Flattened structure for IoT sync
    id: int
    name: str
    encoding: bytes
    
    @field_serializer('encoding')
    def serialize_encoding(self, encoding: bytes, _info):
        return base64.b64encode(encoding).decode('utf-8')

    class Config:
        from_attributes = True
