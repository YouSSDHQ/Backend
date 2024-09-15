from pydantic import BaseModel, Field

class UssdRequest(BaseModel):
    phone_number: str = Field(..., example="+2348078807660", serialization_alias="phoneNumber")
    service_code: str = Field(..., example="*384*23273#", serialization_alias="serviceCode")
    text: str = Field(default="", serialization_alias="text")
    session_id: str = Field(..., example="ATUid_95c5de026e93f5a4d656ae54323276dd", serialization_alias="sessionId")
    network_code: str = Field(..., example="99999", serialization_alias="networkCode")
