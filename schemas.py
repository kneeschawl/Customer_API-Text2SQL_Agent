from pydantic import BaseModel, ConfigDict
from typing import Optional

class CustomerBase(BaseModel):
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[float] = None

class CustomerCreate(CustomerBase):
    customerNumber: int

class CustomerUpdate(BaseModel):
    customerName: Optional[str] = None
    contactLastName: Optional[str] = None
    contactFirstName: Optional[str] = None
    phone: Optional[str] = None
    # All fields are optional here for partial updates

class CustomerOut(CustomerBase):
    customerNumber: int
    model_config = ConfigDict(from_attributes=True)