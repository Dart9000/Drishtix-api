from dotenv import load_dotenv
import requests
import json
import os

class Whatsapp_Cloud_API:
  
  #------------------------------------------------------------------------------------------
   
  '''
  .env file required with 
  PHONE_ID = <Value>
  TOKEN = <Value>
  '''
  
  #------------------------------------------------------------------------------------------
  
  def __init__(self):
    load_dotenv()
    phone_id = os.getenv("PHONE_ID")
    token = os.getenv("TOKEN")
    self.__url__ = "https://graph.facebook.com/v13.0/"+ phone_id +"/messages"
    self.__headers__ = {
      'Authorization' : 'Bearer '+token,
      'Content-Type'  : 'application/json'
    }
    
  #------------------------------------------------------------------------------------------
  
  def validate(self,text):
    return ('messaging_product' in text)
    
  #------------------------------------------------------------------------------------------
  
  def alert(self,Phone,Image_Link,Name,Profile_Link,Address,Time):
    payload = json.dumps({
      "messaging_product": "whatsapp",
      "to": Phone,
      "type": "template",
      "template": {
        "name": "alert",
        "language": {
          "code": "en"
        },
        "components": [
          {
            "type": "header",
            "parameters": [
              {
                "type" : "image",
                "image": {
                  "link": Image_Link
                }
              }
            ]
          },
          {
            "type": "body",
            "parameters": [
              {
                "type": "text",
                "text": Name
              },
              {
                "type": "text",
                "text": Profile_Link
              },
              {
                "type": "text",
                "text": Address
              },
              {
                "type": "text",
                "text": Time
              }
            ]
          }
        ]
      }
    })
    response = requests.request("POST", self.__url__, headers=self.__headers__, data=payload)
    print(response.text)
    return self.validate(response.text)
    
  #------------------------------------------------------------------------------------------


'''  
ILLUSTRATION
------------

Phone = "919549408165"
Image_Link = "https://avatars.githubusercontent.com/u/68856476?s=400&u=3d5c281a14da0a6d2efa7cd9345e30d3e872ab8f&v=4"
Name = "Garvit Chouhan"
Profile_Link = "https://avatars.githubusercontent.com/u/68856476?s=400&u=3d5c281a14da0a6d2efa7cd9345e30d3e872ab8f&v=4"
Address = "Udaipur Rajasthan"
Time = "5:16 pm 17/06/2022"

api = Whatsapp_Cloud_API()
print(api.alert(Phone,Image_Link,Name,Profile_Link,Address,Time))

'''
