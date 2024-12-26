
from sqlalchemy import Column, Integer, String,Text, Float, Boolean, ForeignKey,Enum,DateTime,Time,event
from sqlalchemy.event import listens_for
from sqlalchemy.orm import relationship,validates,backref
from saleapp import db, app
from enum import Enum as UserEnum, unique
from wtforms import ValidationError
from flask import flash,session
from markupsafe import Markup
from flask_login import UserMixin
from datetime import datetime,timedelta

class UserRole(UserEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"

class Flight_Status(UserEnum):
    CHUA_CAT_CANH = "Chưa cất cánh"
    DA_CAT_CANH = "Đã cất cánh"
    HUY = "Hủy"
    TRE = "Trễ"

class Flight_Class(UserEnum):
    HANG_1="Hạng 1"
    HANG_2="Hạng 2"

TICKET_PRICES = {
    Flight_Class.HANG_1: 500.000,
    Flight_Class.HANG_2: 300.000,
    }



class User(db.Model,UserMixin):
    __tablename__ = 'user'
    id = Column(String(100), primary_key=True)
    name=Column(String(50),nullable=False)
    username=Column(String(50),nullable=False,unique=True)
    password=Column(String(150),nullable=False)
    email=Column(String(100),nullable=True,unique=True)
    phone_number = Column(String(50),nullable=True,unique=True)
    avatar=Column(String(100),nullable=True)
    user_role=Column(Enum(UserRole), default=UserRole.CUSTOMER)

    @event.listens_for(db.session, 'before_flush')
    def generate_User_id(session, flush_context, instances):
        for instance in session.new:
            if isinstance(instance, User) and instance.id is None:
                user_role = instance.user_role

                last_user = db.session.query(User).order_by(User.id.desc()).first()

                if last_user:
                    last_id_number = int(last_user.id[3:])
                    new_id_number = last_id_number + 1
                else:
                    new_id_number = 1

                if user_role == UserRole.ADMIN:
                    instance.id = f"ADM{new_id_number:03d}"  # ID dành cho Admin
                elif user_role == UserRole.CUSTOMER:
                    instance.id = f"CUS{new_id_number:03d}"  # ID dành cho Customer
                else:
                    instance.id = f"US{new_id_number:03d}"  # ID mặc định cho User

    def __str__(self):
        return self.name


class Airport(db.Model):
    __tablename__ = 'airports'
    id = db.Column(db.String(100), primary_key=True)  # Mã sân bay
    name = db.Column(db.String(100), nullable=False,unique=True)  # Tên sân bay
    city = db.Column(db.String(100), nullable=False)  # Thành phố
    country = db.Column(db.String(100), nullable=False,default='Việt Nam')  # Quốc gia

    def __repr__(self):
        return f' {self.name} ({self.id}), {self.country}'


class flight_airport(db.Model):
    __tablename__ = 'flight_airport'
    STT = db.Column(db.Integer, autoincrement=True )
    flight_id = db.Column(db.String(100), db.ForeignKey('flights.id'), primary_key=True)
    airport_id = db.Column(db.String(100), db.ForeignKey('airports.id'), primary_key=True)
    stopover_time = db.Column(db.Integer)

    def __repr__(self):
        return f' {self.stopover_time}'


class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.String(100), primary_key=True)  # Mã tuyến bay
    departure_airport_id = db.Column(db.String(100), db.ForeignKey('airports.id'), nullable=False)  # Mã sân bay đi
    arrival_airport_id = db.Column(db.String(100), db.ForeignKey('airports.id'), nullable=False)  # Mã sân bay đến
    departure_airport = db.relationship('Airport', foreign_keys=[departure_airport_id])
    arrival_airport = db.relationship('Airport', foreign_keys=[arrival_airport_id])
    name = db.Column(db.String(100),unique=True)

    @event.listens_for(db.session, 'before_flush')
    def generate_route_id(session, flush_context, instances):
        for instance in session.new:
            if isinstance(instance, Route) and instance.id is None:
                last_route = db.session.query(Route).order_by(Route.id.desc()).first()
                if last_route:
                    last_id_number = int(last_route.id[2:])
                    new_id_number = last_id_number + 1
                    instance.id = f"RT{new_id_number:03d}"
                else:
                    instance.id = "RT001"

    @event.listens_for(db.session, 'before_flush')
    def generate_route_name(session, flush_context, instances):
        for instance in session.new:
            if isinstance(instance, Route) and instance.name is None:
                if instance.departure_airport and instance.arrival_airport:
                    departure_airport_name = instance.departure_airport.name
                    arrival_airport_name = instance.arrival_airport.name
                    instance.name = f"{departure_airport_name} - {arrival_airport_name}"

                    existing_route = db.session.query(Route).filter_by(name=instance.name).first()
                    if existing_route:
                        raise ValidationError(f"Tuyến bay '{instance.name}' đã tồn tai. Vui lòng tạo tuyến bay mới!")

    def __repr__(self):
        return f' {self.name}'


class Flight(db.Model):
    __tablename__ = 'flights'
    id = db.Column(db.String(100), primary_key=True)
    route_id = db.Column(db.String(50), db.ForeignKey('routes.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    seat_count_class_1 = db.Column(db.Integer,nullable=False)
    seat_sell_class_1 = db.Column(db.Integer,nullable=True,default=0)
    seat_price_class_1 = db.Column(db.Float,nullable=True)
    seat_count_class_2 = db.Column(db.Integer,nullable=False)
    seat_sell_class_2 = db.Column(db.Integer,nullable=True,default=0)
    seat_price_class_2 = db.Column(db.Float,nullable=True)
    route = db.relationship('Route', backref='flights', lazy=True)
    airports = db.relationship('Airport',secondary='flight_airport',lazy='subquery',backref=backref('flightss',lazy=True))
    flight_status = db.Column(Enum(Flight_Status))

    @property
    def flight_status_display(self):
        return self.flight_status.value if self.flight_status else "Chưa xác định"

    @event.listens_for(db.session, 'before_flush')
    def generate_flight_id(session, flush_context, instances):
        for instance in session.new:
            if isinstance(instance, Flight) and instance.id is None:
                last_flight = db.session.query(Flight).order_by(Flight.id.desc()).first()
                if last_flight:
                    last_id_number = int(last_flight.id[2:])
                    new_id_number = last_id_number + 1
                    instance.id = f"VN{new_id_number:03d}"
                else:
                    instance.id = "VN001"


    @validates('departure_time')
    def validate_departure_time(self, key, departure_time):
        if departure_time < datetime.now():
            raise ValidationError("Thời gian lập lịch phải lớn hơn thời gian hiện tại!")
        return departure_time

    @event.listens_for(db.session, 'after_commit')
    def after_commit(session):
        for instance in session.new:
            if isinstance(instance, Flight):
                # Lưu id của ticket vào session sau khi commit vào cơ sở dữ liệu
                session['flight_id'] = instance.id
                print(f"Ticket ID saved to Flask session: {instance.id}")

    def __str__(self):
        return f'{self.id} - {self.departure_time} '


class FlightSchedule(Flight):
    __tablename__ = 'flight_schedules'
    schedule_id = db.Column(db.String(100), primary_key=True)  # Mã lịch chuyến bay
    flight_id = db.Column(db.String(100), db.ForeignKey('flights.id'), nullable=False)  # Mã chuyến bay
    schedule_date = db.Column(db.Date, nullable=False)  # Ngày lịch chuyến bay
    flight = db.relationship('Flight',backref='flight_schedule',lazy=True)

    def __repr__(self):
        return f'FlightSchedule {self.schedule_date}'


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.String(100), primary_key=True)
    # seat_id  = db.Column(db.String(100),db.ForeignKey('seats.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(50),nullable=True)
    customer_count=db.Column(db.Integer,nullable=True)
    price = db.Column(db.Float,nullable=True)
    payment_id = db.Column(db.String(50),db.ForeignKey('payments.id'),nullable=True)
    email=db.Column(db.String(50))

    # @event.listens_for(db.session, 'before_flush')
    # def generate_ticket_id(session, flush_context, instances):
    #     for instance in session.new:
    #         if isinstance(instance, Ticket) and instance.id is None:
    #             last_ticket = db.session.query(Ticket).order_by(Ticket.id.desc()).first()
    #             if last_ticket:
    #                 last_id_number = int(last_ticket.id[3:])
    #                 new_id_number = last_id_number + 1
    #                 instance.id = f"OUA{new_id_number:04d}"
    #             else:
    #                 instance.id = "OUA0001"


    @property
    def ticket_class_display(self):
        return self.ticket_class.value if self.ticket_class else "Chưa xác định"

    def __repr__(self):
        return f'Ticket {self.id}'


class Seat(db.Model):
    __tablename__ = 'seats'
    id = db.Column(db.String(100), primary_key=True)
    flight_id = db.Column(db.String(100), db.ForeignKey('flights.id'), nullable=False)
    seat_number = db.Column(db.String(50), nullable=False)
    flight = db.relationship('Flight', backref='seats',lazy=True)

    def __repr__(self):
        return f'<Seat {self.seat_number}>'


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.String(100), primary_key=True)  # Mã thanh toán
    payment_method = db.Column(db.String(50), nullable=False,default="Chuyến khoản")  # Phương thức thanh toán (Ví dụ: Tiền mặt, Thẻ tín dụng, ... )
    amount = db.Column(db.Float, nullable=False)  # Số tiền thanh toán
    # payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)  # Trạng thái thanh toán
    payment_date = db.Column(db.DateTime, default=datetime.now())  # Thời gian thanh toán


class Configuration(db.Model):
    __tablename__ = 'configurations'
    id = db.Column(db.String(100), primary_key=True)
    num_airports = db.Column(db.Integer, default=10)
    min_flight_time = db.Column(db.Integer,  default=30)
    max_stopover_airports = db.Column(db.Integer,  default=2)
    min_stopover_time = db.Column(db.Integer,  default=20)
    max_stopover_time = db.Column(db.Integer,  default=30)
    time_book_tickets = db.Column(db.Integer, default=12)
    time_sell_tickets = db.Column(db.Integer, default=4)

    def __repr__(self):
        return f'<Configuration {self.id}>'

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.String(50),primary_key=True)
    lastname = db.Column(db.String(100),nullable=True)
    fullname = db.Column(db.String(100),nullable=True)
    phone_number = db.Column(db.String(100),nullable=True)
    email = db.Column(db.String(100),nullable=True)
    identity_number = db.Column(db.String(100),nullable=True)
    payment_date = db.Column(db.DateTime,nullable=True)
    user_id = db.Column(db.String(100),db.ForeignKey('user.id'),nullable=True)
    flight_id_1 = db.Column(db.String(100),db.ForeignKey('flights.id'),nullable=True)
    flight1 =db.relationship('Flight',foreign_keys=[flight_id_1])
    ticket_flight_1 = db.Column(db.String(50),nullable=True)
    flight_id_2 = db.Column(db.String(100), db.ForeignKey('flights.id'), nullable=True)
    flight2 =db.relationship('Flight',foreign_keys=[flight_id_2])
    ticket_flight_2 = db.Column(db.String(50),nullable=True)
    ticket_id = db.Column(db.String(50),db.ForeignKey('tickets.id'),nullable=True)
    ticket=db.relationship('Ticket',backref='customers',lazy=True)
    # @event.listens_for(db.session, 'before_flush')
    # def generate_customer_id(session, flush_context, instances):
    #     for instance in session.new:
    #         if isinstance(instance, Customer) and instance.id is None:
    #             last_customer = db.session.query(Customer).order_by(Customer.id.desc()).first()
    #             if last_customer:
    #                 last_id_number = int(last_customer.id[3:])
    #                 new_id_number = last_id_number + 1
    #                 instance.id = f"CUS{new_id_number:04d}"
    #             else:
    #                 instance.id = "CUS0001"

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()  # tạo mới database mới dùng

        # import hashlib
        # password = str(hashlib.md5('123456'.encode('utf-8')).digest())
        # u = User(name='y',username='nhanvien',password=password,
        #          user_role=UserRole.USER,
        #          avatar='https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg')
        # db.session.add(u)
        # db.session.commit()
