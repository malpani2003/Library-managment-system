from typing import List, Annotated, Optional
from fastapi import FastAPI, Path, Query, status, HTTPException, Request
from bson.objectid import ObjectId
from models.studentModel import Student
from models.updateStudentModel import UpdatedStudent
from db import collection
import redis
from starlette.responses import Response
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import dotenv_values
import os

config = dotenv_values(os.getcwd() + "/.env")

app = FastAPI()

# Setup Redis connection
try:
    redis_client = redis.Redis(host=config["REDIS_HOST"], port=config["REDIS_PORT"], db=0,password=config["REDIS_PASSWORD"])
    if redis_client.ping():
        print("Redis is connected")
    else:
        print("Redis is not connected")
except Exception as e:
    print(e)

# Rate Limiting Middleware
class RateLimitMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        print(request.headers)
        # Get user_id from Headers
        user_id = request.headers.get("user_id")
        if user_id:
            # If User id exist then increment the rate
            self.change_rate_limit(user_id=user_id)
            response = await call_next(request)
        else:
            # Not exist then generate error s response
            response = Response("No user_id header present", status_code=400)
        return response

    def change_rate_limit(self, user_id: str):
        key = f"rate_limit:{user_id}"
        # Check if the key exists
        if redis_client.exists(key):
            # If key exists, increment the key value
            redis_client.incr(name=key)
        else:
            # If key doesn't exist, set it with an expiry for the next day
            redis_client.setex(name=key,time=timedelta(days=1),value=1)
    
    # def check_rate_limit(self,user_id:str,key:str):
    #     value=redis_client.get(key)
    #     if value >=10:   # Limit of 10
    #         print("Rate Limit Execced")
    #     else:
    #         return

# Add RateLimitMiddleware to the app
app.add_middleware(RateLimitMiddleware)

# Route to Create Student
@app.post("/students", status_code=status.HTTP_201_CREATED, description="API to create a student in the system. All fields are mandatory and required while creating the student in the system.")
def create_students(data: Student):
    try:
        x = collection.insert_one(data.dict())
        return {"id": str(x.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to Get Students Details based on _id
@app.get("/students/{id}", status_code=status.HTTP_200_OK, description="sample response")
def fetch_student(id: Annotated[str, Path(..., description="The ID of the student previously created.")]):
    try:
        objInstance = ObjectId(id)
        studentData = collection.find_one({"_id": (objInstance)}, {"_id": 0})
        return studentData
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to Get Students based on Country and age value
@app.get("/students", status_code=status.HTTP_200_OK, description=" An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below")
def list_students(country: str = Query(None, description="To apply filter of country. If not given or empty, this filter should be applied."), age: int = Query(None, description="Only records which have age greater than equal to the provided age should be present in the result. If not given or empty, this filter should be applied.")):
    try:
        query = {}
        if country:
            query["address.country"] = country
        if age:
            query["age"] = {"$gte": age}

        students = list(collection.find(query, {"_id": 0}))
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to Delete Students Details
@app.delete("/students/{id}", status_code=status.HTTP_200_OK)
def delete_student(id: str = Path(...)):
    try:
        objInstance = ObjectId(id)
        studentData = collection.find_one({"_id": (objInstance)}, {"_id": 0})
        if studentData:
            collection.delete_one({"_id": objInstance})
            return {}
        else:
            raise HTTPException(status_code=404, detail="No Student Present")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to Update Student Details
@app.patch("/students/{id}", status_code=status.HTTP_204_NO_CONTENT, description="API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database")
def update_student(id: str = Path(...), update_obj2: UpdatedStudent = None):
    try:
        if update_obj2 is not None:
            update_obj = update_obj2.dict(exclude_unset=True)
        else:
            update_obj = {}

        objInstance = ObjectId(id)

        # Find Student if present or not
        studentData = collection.find_one({"_id": objInstance}, {"_id": 0})
        if studentData:
            # If present then check which values are absent or present and update with older one if not present
            if "name" not in update_obj:
                update_obj["name"] = studentData.get("name")
            if "age" not in update_obj:
                update_obj["age"] = studentData.get("age")
            if "address" not in update_obj:
                update_obj["address"] = studentData.get("address", {})
            else:
                address = update_obj.get("address", {})
                update_obj["address"] = {
                    "city": address.get("city", studentData["address"].get("city")),
                    "country": address.get("country", studentData["address"].get("country"))
                }

            collection.update_one({"_id": objInstance}, {"$set": update_obj})
            return {}
        else:
            raise HTTPException(status_code=404, detail="No Student Present")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
