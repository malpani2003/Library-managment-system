from pydantic import BaseModel, validator

class StudentAddress(BaseModel):
    city:str
    country:str

class Student(BaseModel):
    name: str
    age: int
    address: StudentAddress

