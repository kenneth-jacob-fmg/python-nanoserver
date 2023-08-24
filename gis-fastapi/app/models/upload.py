from pydantic import BaseModel

class Upload(BaseModel):
    referralId: int
    enquiryId: int
    path: str
    emailBodyContent:str