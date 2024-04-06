from typing import List,Annotated,Optional
from fastapi import FastAPI,Path,Query,status,HTTPException
from bson.objectid import ObjectId
from models.studentModel import Student
from models.updateStudentModel import UpdatedStudent
from db import collection

app = FastAPI() 

# Route to Create Student
@app.post("/students",status_code=status.HTTP_201_CREATED,description="API to create a student in the system. All fields are mandatory and required while creating the student in the system.")
def create_students(data:Student):
    try:
        x = collection.insert_one(data.dict())
        return {"id": str(x.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# Route to Get Students Details based on _id
@app.get("/students/{id}",status_code=status.HTTP_200_OK,description="sample response")
def fetch_student(id:Annotated[str, Path(...,description="The ID of the student previously created.")]):
    try:
        objInstance = ObjectId(id)
        studentData=collection.find_one({"_id":(objInstance)},{"_id":0})
        return studentData
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Route to Get Students based on Country and age value
@app.get("/students",status_code=status.HTTP_200_OK,description=" An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below")
def list_students(country:str = Query(None, description="To apply filter of country. If not given or empty, this filter should be applied."), age: int = Query(None, description="Only records which have age greater than equal to the provided age should be present in the result. If not given or empty, this filter should be applied.")):
    try:
        query = {}
        if country:
            query["address.country"] = country
        if age:
            query["age"] = {"$gte": age}

        students = list(collection.find(query, {"_id": 0}))
        return students
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# Route to Delete Students Details
@app.delete("/students/{id}",status_code=status.HTTP_200_OK)
def delete_student(id: str = Path(...)):
    try:
        # return str(id)
        objInstance = ObjectId(id)
        studentData=collection.find_one({"_id":(objInstance)},{"_id":0})
        if studentData:
            collection.delete_one({"_id":objInstance})
            return {}
        else:
            raise HTTPException(status_code=404, detail="No Student Present")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Route to Updated Student Details
@app.patch("/students/{id}",status_code=status.HTTP_204_NO_CONTENT,description="API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database")
def update_student(id: str = Path(...),update_obj2:UpdatedStudent=None):
    try:
        if update_obj2 is not None:
            update_obj=update_obj2.dict()
        else:
            update_obj={}

        objInstance = ObjectId(id)
        
        # Update the Data 
        studentData=collection.find_one({"_id":(objInstance)},{"_id":0})
        if studentData:
            collection.update_one({"_id":objInstance},{"$set":update_obj}) 
            return {}
        else:
            raise HTTPException(status_code=404, detail="No Student Present")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))