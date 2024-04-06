from pydantic import BaseModel, validator
from typing import Optional

class UpdateStudentAddress(BaseModel):
    city:Optional[str]=None
    country:Optional[str]=None
    
class UpdatedStudent(BaseModel):
    name:Optional[str]=None
    age: Optional[int]=None
    address: Optional[UpdateStudentAddress]=None
