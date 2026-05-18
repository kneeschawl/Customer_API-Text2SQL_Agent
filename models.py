from sqlalchemy import Column, Integer, String, Numeric
from database import Base

class Customer(Base):
    __tablename__ = "customers"
    customerNumber = Column(Integer, primary_key=True)

class Order(Base):
    __tablename__ = "orders"
    orderNumber = Column(Integer, primary_key=True)

class Product(Base):
    __tablename__ = "products"
    productCode = Column(String, primary_key=True)

class Employee(Base):
    __tablename__ = "employees"
    employeeNumber = Column(Integer, primary_key=True)

class Office(Base):
    __tablename__ = "offices"
    officeCode = Column(String, primary_key=True)

class Payment(Base):
    __tablename__ = "payments"
    checkNumber = Column(String, primary_key=True)

class OrderDetail(Base):
    __tablename__ = "orderdetails"
    orderNumber = Column(Integer, primary_key=True)
    productCode = Column(String, primary_key=True)

class ProductLine(Base):
    __tablename__ = "productlines"
    productLine = Column(String, primary_key=True)