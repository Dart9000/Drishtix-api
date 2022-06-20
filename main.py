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


#Loading Database
load_dotenv()
URI = os.getenv("MONGO_URI")
client    = MongoClient(URI)
database  = client.Drishtix.Dataset
criminal  = client.Drishtix.Criminal    

#Modules
IST = pytz.timezone('Asia/Kolkata')
api = Whatsapp_Cloud_API()
face = Face()

app = FastAPI()

#CORS enable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Info(BaseModel):
  Address : str
  Phone : str


@app.get("/test")
async def test()
    return {status: "Working"}

@app.post("/encode")
async def encode(file: UploadFile = File(...)):
    extension = '.'+file.filename.split('.')[-1]
    temp = tempfile.NamedTemporaryFile(suffix=extension)
    with open(temp.name, 'wb') as image:
        content = await file.read()
        image.write(content)
        image.close()
    encoding = face.encode(temp.name)
    print(type(encoding))
    temp.close()
    response.headers.add('Access-Control-Allow-Origin', '*')
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
    data_arr = [ np.array(i) for i in data["value"] ]
    vector_arr = [ np.array(i) for i in data["key"] ]
    res = face.search(temp.name, data_arr, vector_arr)
    for i in res:
      packet = criminal.find_one( {"_id": ObjectId(i)} )
      Name         = packet["name"]
      Image_Link   = "drishtix-api.herokuapp.com/snap?"+temp.name
      Profile_Link = "sampleapp.com/profile/"+str(i) 
      Address      = Address
      Contact      = "91" + Phone
      Time         = str(datetime.now(IST))
      api.alert(Contact,Image_Link,Name,Profile_Link,Address,Time)
    temp.close()    
    return {"Task" : "Query Search", "Status" : True}

@app.get("/snap")
def pdf(path: str):
    extension = path.split('.')[-1]
    if extension not in ['jpg','png','jpeg'] : raise HTTPException(status_code=404, detail="Not Authorized to access this Resource/API")
    return FileResponse(path)
