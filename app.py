from typing import List,Annotated
from fastapi import FastAPI,Path
from pymongo import MongoClient
from bson.objectid import ObjectId
from pydantic import BaseModel, validator

app = FastAPI()
url = ""
client = MongoClient("localhost", 27017)
databaseName = "library-managment-system"
collectionName = "student"

if databaseName in client.list_database_names():
    print("Database Already Exist")

db = client[databaseName]
collection = db[collectionName]

class Student(BaseModel):
    name: str
    age: int
    address: dict

    @validator("address")
    def validate_address(cls, value):
        if not isinstance(value, dict):
            raise ValueError("Address must be a dictionary")
        if not all(key in value for key in ("city", "country")):
            raise ValueError("Address must contain 'city' and 'country'")
        return value

@app.post("/student")
def home(data:Student):
    try:
        # return data
        student_data = Student(**data)
        x = collection.insert_one(student_data.dict())
        return {"id": str(x.inserted_id)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/students/{id}")
def read_student_by_id(id:str):
    try:
        # return str(id)
        objInstance = ObjectId(id)
        studentData=collection.find_one({"_id":(objInstance)},{"_id":0})
        if studentData:
            return studentData
        else:
            return {"error":True,"msg":"No Student Present"}
    except Exception as e:
        return {"error":True,"msg":str(e)} 



@app.get("/students")
def read_student_by_id(country:str|None=None,age:int|None=0):
    try:
        # return str(id)
        if country is not None:
            objInstance = ObjectId(id)
            studentData=collection.find_one({"_id":(objInstance)},{"_id":0})
            if studentData:
                return studentData
            else:
                return {"error":True,"msg":"No Student Present"}
    except Exception as e:
        return {"error":True,"msg":str(e)} 


@app.delete("/students/{id}")
def delet_student_by_id(id:str):
    try:
        # return str(id)
        objInstance = ObjectId(id)
        studentData=collection.find_one({"_id":(objInstance)},{"_id":0})
        if studentData:
            collection.delete_one({"_id":objInstance})
            return {}
        else:
            return {"error":True,"msg":"No Student Present"}
    except Exception as e:
        return str(e) 

@app.patch("/students/{id}")
def update_student_by_id(id:str,update_obj2:object| None):
    try:
        # return str(id)
        update_obj=update_obj2.dict()
        objInstance = ObjectId(id)
        studentData=collection.find_one({"_id":(objInstance)},{"_id":0})
        if studentData:
            collection.update_one({"_id":objInstance},{"$set":update_obj}) 
            return {}
        else:
            return {"error":True,"msg":"No Student Present"}
    except Exception as e:
        return str(e) 

@app.get("/students", response_model=List[Student])
def read_students():
    try:
        students = list(collection.find({}, {"_id": 0}))
        return students
    except Exception as e:
        return {"error": str(e)}
