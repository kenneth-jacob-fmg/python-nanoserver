from datetime import datetime
from pydantic import BaseModel

# https://www.nextgendbyd.com.au/wp-content/uploads/2021/03/sample-referral-create-webhook.json

class Organisation(BaseModel):
    id: int
    name: str
    utilityId: int

class Enquiry(BaseModel):
    id: int
    geometry: object

class Referral(BaseModel):
    id:int
    createdAt: datetime
    status: str
    sequenceNumber: int
    Organisation: Organisation
    Enquiry: Enquiry


    
