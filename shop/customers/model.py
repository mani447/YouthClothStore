from shop import db, login_manager
from datetime import datetime
from flask_login import UserMixin
import json

@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)

class Register(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), unique= False)
    country = db.Column(db.String(50), unique=False)
    username = db.Column(db.String(50), unique= True)
    email = db.Column(db.String(50), unique= True)

    city = db.Column(db.String(50), unique= False)
    contact = db.Column(db.String(50), unique= False)
    password = db.Column(db.String(200), unique=False)
    address = db.Column(db.String(50), unique= False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    zipcode = db.Column(db.String(50), unique=False)

    def __repr__(self):
        return '<Register %r>' % self.name


class encode(db.TypeDecorator):
    impl = db.Text
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        else:
            return '{}'
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        else:
            return {}

class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, unique=False, nullable=False)
    orders = db.Column(encode)

    def __repr__(self):
        return'<CustomerOrder %r>'


db.create_all()




    


