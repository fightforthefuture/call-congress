from sqlalchemy import (Column, Integer, String, DateTime)
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()

def hash_phone(number):
    # takes phone number and returns 64 charachter string
    return hashlib.sha256(number).hexdigest()

def to_dict(model):
    d = model.__dict__
    d.pop('_sa_instance_state')
    return d
db.Model.to_dict = to_dict 

class Call(db.Model):
    __tablename__ = 'calls'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    status = Column(String(25)) # twilio call status
    length = Column(Integer)  # twilio call time in seconds
    campaign_id = Column(String(10))
    member_id = Column(String(10)) # congress member sunlight identifier
    # user attributes
    user_id = Column(String(64)) # hashed phone number
    zipcode = Column(String(5)) 
    areacode = Column(Integer) # first 3 digits of phone number
    exchange = Column(Integer) # next 3 digits of phone number
    
    def __init__(self, campaign_id, member_id, zipcode, phone_number, status, length):
        self.timestamp = datetime.now()
        self.status = status
        self.length = length
        self.campaign_id = campaign_id
        self.member_id = member_id
        phone_number = phone_number.replace('-', '').replace('.', '')
        self.user_id = hash_phone(phone_number)
        self.areacode = phone_number[:3]
        self.exchange = phone_number[3:6]
        self.zipcode = zipcode

    def __repr__(self):
        return '<Call {}-{}-xxxx to {}>'.format(
            self.areacode, self.exchange, self.member_id)
    
def log_call(db, **kwds):
    db.session.add(Call(**kwds))
    db.session.commit()


def setUp(app):
    db.app = app
    db.drop_all()
    db.create_all()    
    
def tearDown(app):
    db.app = app
    db.drop_all()
    
if __name__ == "__main__":
    # initialize db
    from app import app
    setUp(app)