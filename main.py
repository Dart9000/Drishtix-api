from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from alert_module import Whatsapp_Cloud_API
from face_module import Face
from pymongo import MongoClient
from dotenv import load_dotenv  
from bson.objectid import ObjectId
from pydantic import BaseModel
from datetime import datetime
import pytz
import os
import tempfile
import numpy as np
import time


#Loading Database
load_dotenv()
URI = os.getenv("MONGO_URI")
client    = MongoClient(URI)
database  = client.drishtiDB.datasets
criminal  = client.drishtiDB.criminals    

#Modules
IST = pytz.timezone('Asia/Kolkata')
api = Whatsapp_Cloud_API()
face = Face()

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Info(BaseModel):
  Address : str
  Phone : str


@app.post("/encode")
async def encode(file: UploadFile = File(...)):
    extension = '.'+file.filename.split('.')[-1]
    temp = tempfile.NamedTemporaryFile(suffix=extension)
    with open(temp.name, 'wb') as image:
        content = await file.read()
        image.write(content)
        image.close()
    encoding = face.encode(temp.name)
    temp.close()
    return {"Task" : "Image Encoding", "Status" : True, "encoding" : list(encoding)}



@app.post("/search")
async def search(Phone : str, Address : str, file: UploadFile = File(...)):
    extension = '.'+file.filename.split('.')[-1]
    temp = tempfile.NamedTemporaryFile(suffix=extension)
    with open(temp.name, 'wb') as image:
        content = await file.read()
        image.write(content)
        image.close()
    data = database.find_one({"_id" : "dataset"})
    data_arr = []
    vector_arr = []
    length = len(data["key"])
    for i in range(length):
      if data["key"][i] != "":
        vector_arr.append(np.array([float(n) for n in data["key"][i]]))
        data_arr.append(data["value"][i])
    res = face.search(temp.name, data_arr, vector_arr)
    print(res)
    for i in res:
      packet = criminal.find_one( {"_id": ObjectId(i)} )
      Name         = packet["name"]
      Image_Link   = "drishtix-api.herokuapp.com/snap?path="+temp.name
      Profile_Link = "sampleapp.com/profile/"+str(i) 
      Address      = Address
      Contact      = "91" + Phone
      Time         = str(datetime.now(IST))
      print(Contact,Image_Link,Name,Profile_Link,Address,Time)
      api.alert(Contact,Image_Link,Name,Profile_Link,Address,Time)
    time.sleep(0.5)
    temp.close() 
    return {"Task" : "Query Search", "Status" : True}

@app.get("/snap")
def pdf(path: str):
    print("test :",path)
    extension = path.split('.')[-1]
    if extension not in ['jpg','png','jpeg'] : raise HTTPException(status_code=404, detail="Not Authorized to access this Resource/API")
    return FileResponse(path)
