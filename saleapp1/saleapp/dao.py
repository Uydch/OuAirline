from sqlalchemy.exc import NoResultFound
from saleapp import app,mail
from saleapp.models import User, db, Flight, Route, Airport, Customer, Ticket,Payment,Seat,Flight_Status
import hashlib
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from flask_mail import Mail,Message
from flask import render_template,session
import random

def auth_user(username,password):
    password =str(hashlib.md5(password.strip().encode('utf-8')).digest())

    return User.query.filter(User.username.__eq__(username.strip())
                             ,User.password.__eq__(password)).first()


def register(name, username, password,email, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).digest())
    u = User(name=name, username=username.strip(), password=password,email=email, avatar=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def lay_thong_tin_chuyen_bay_theo_id(flight_id):
    flight = Flight.query.filter(Flight.id == flight_id).first()

    if flight:
        return flight  # Trả về đối tượng chuyến bay nếu tìm thấy
    else:
        return None

def generate_id( model, prefix, id_length):
    last_object = db.session.query(model).order_by(model.id.desc()).first()
    if last_object:
        last_id_number = int(last_object.id[len(prefix):])
        new_id_number = last_id_number + 1
        new_id = f"{prefix}{new_id_number:0{id_length}d}"
    else:
        new_id = f"{prefix}{1:0{id_length}d}"

    return new_id

def tim_tuyen_bay_theo_diem(diemdi, diemden,ngaydi):
    diemdi = diemdi.strip().capitalize()
    diemden = diemden.strip().capitalize()
    tuyen_bay = diemdi + " - " + diemden
    ngaydi = datetime.strptime(ngaydi, '%Y-%m-%d').date()
    return Flight.query.join(Route).filter(
        Route.name.__eq__(tuyen_bay),
        db.func.DATE(Flight.departure_time).__eq__(ngaydi) ).all()

def ngay_ve(diemdi, diemden,ngayden):
    tuyen_bay = diemden + " - " + diemdi
    ngayden = datetime.strptime(ngayden, '%Y-%m-%d').date()
    return Flight.query.join(Route).filter(
        Route.name.__eq__(tuyen_bay),db.func.DATE(Flight.departure_time).__eq__(ngayden)).all()

def get_all_departure_airports(db_session):
    routes = db_session.query(Route).options(
        joinedload(Route.departure_airport)).all()
    departure_airports = set()
    for route in routes:
        if route.departure_airport:
            departure_airports.add(route.departure_airport.name)
    return list(departure_airports)


def get_all_arrival_airports(db_session):
    routes = db_session.query(Route).options(
        joinedload(Route.arrival_airport)
    ).all()
    arrival_airports = set()
    for route in routes:
        if route.arrival_airport:
            arrival_airports.add(route.arrival_airport.name)
    return list(arrival_airports)


def send_payment_success_email(user_email, total_price,adult_infor,child_info,infant_info):
    subject = 'OuAirlines - Xác nhận đặt vé thành công'
    date_time = datetime.now()
    session['date_time'] = date_time
    pay_date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
    today = datetime.now().strftime('%Y%m%d')
    random_number = random.randint(1000000, 9999999)
    payment_number = f"{today}{random_number}"
    session['payment_number'] = payment_number
    message = render_template('email.html',adult_infor=adult_infor,
                              total_price=total_price,pay_date_time=pay_date_time,
                              child_info=child_info,infant_info=infant_info,payment_number=payment_number)
    msg = Message(subject, recipients=[user_email], html=message)
    try:
        mail.send(msg)
        print(f"Email đã gửi thành công tới {user_email}")
    except Exception as e:
        print(f"Không thể gửi email: {e}")


def customer_infor(customer_id,lastname, fullname, phone_number, email,identity_number,
                   payment_date,user_id,flight_id_1,ticket_flight_1,flight_id_2,ticket_flight_2,ticket_id):
    customer = Customer(id=customer_id,lastname=lastname,fullname=fullname,phone_number=phone_number,
                        email=email,identity_number=identity_number,payment_date=payment_date,
                        user_id=user_id,flight_id_1=flight_id_1,ticket_flight_1=ticket_flight_1,
                        flight_id_2=flight_id_2,ticket_flight_2=ticket_flight_2,ticket_id=ticket_id)
    db.session.add(customer)
    db.session.commit()

def ticket_infor(ticket_id,username, customer_name,customer_count,price, payment_id,email):
    ticket = Ticket(id=ticket_id,username=username,customer_name=customer_name,
                    customer_count=customer_count,price=price,payment_id=payment_id,email=email)
    db.session.add(ticket)
    db.session.commit()

def payment_infor(payment_id,payment_method,amount,payment_date):
    payment=Payment(id=payment_id,payment_method=payment_method,amount=amount,payment_date=payment_date)
    db.session.add(payment)
    db.session.commit()

def seat_infor(seat_id,flight_id,seat_number):
    seat = Seat(id=seat_id,flight_id=flight_id,seat_number=seat_number)
    db.session.add(seat)
    db.session.commit()

def count_flight_by_route():
    return db.session.query(Route.id,Route.name, func.count(Flight.id))\
           .join(Flight, Flight.route_id.__eq__(Route.id)).group_by(Route.id).all()
def tinh_tong_tien_theo_tuyen_bay(month=None, year=None,route_name=None):
    # Truy vấn tổng tiền theo tên tuyến bay người dùng nhập
    query= db.session.query(
        Route.id,
        Route.name,
        func.sum((Flight.seat_sell_class_1*Flight.seat_price_class_1)+(Flight.seat_sell_class_2*Flight.seat_price_class_2)).label('total_amount')
    ).join(Flight, Flight.route_id.__eq__(Route.id))
    query = query.filter(Flight.flight_status == Flight_Status.DA_CAT_CANH)
    if route_name:
     query=query.filter(Route.name.__eq__(route_name))  # Lọc theo tên tuyến bay người dùng nhập
    if month and year:
        query = query.filter(
            func.month(Flight.arrival_time) == month,
            func.year(Flight.arrival_time) == year
        )
    elif month:  # Nếu chỉ có tháng thì không quan tâm đến năm
        query = query.filter(func.month(Flight.arrival_time) == month)
    elif year:  # Nếu chỉ có năm thì không quan tâm đến tháng
        query = query.filter(func.year(Flight.arrival_time) == year)
    return query.group_by(Route.id, Route.name).all()
# Từ bảng route -> lọc ra những name= route_name, lấy những thằng này lọc theo ngày -> Khi tìm được những thằng thõa mãn thì nó sẽ
# group by để tính tổng Sum của amount.
def count_turn_flight_by_route(month=None, year=None, route_name=None):
    # Thực hiện JOIN giữa Route và Flight, lọc các chuyến bay có trạng thái 'Đã cất cánh'
    # Sử dụng GROUP BY để nhóm theo Route và đếm số chuyến bay đã cất cánh
    query = db.session.query(
        Route.id,  # ID của tuyến bay
        Route.name,  # Tên của tuyến bay (hoặc bất kỳ trường nào bạn muốn từ Route)
        func.count(Flight.id).label('flight_count')  # Đếm số lượng chuyến bay đã cất cánh
    ).join(Flight, Flight.route_id.__eq__(Route.id)) # Lấy tất cả kết quả
    query = query.filter(Flight.flight_status == Flight_Status.DA_CAT_CANH)
    if route_name:
        query = query.filter(Route.name.__eq__(route_name))
    if month and year:
        query = query.filter(
            func.month(Flight.arrival_time) == month,
            func.year(Flight.arrival_time) == year
        )
    elif month: query = query.filter(func.month(Flight.arrival_time) == month)
    elif year: query = query.filter(func.year(Flight.arrival_time) == year)
    return query.group_by(Route.id).all()

def update_user_name_by_id(user_id, new_name,username_user,email,phone_user):
    try:
        user = User.query.filter(User.id==user_id).first()  # `.one()` sẽ gây lỗi nếu không tìm thấy người dùng

        user.name = new_name.strip()
        user.username = username_user.strip()
        user.email = email
        user.phone_number = phone_user
        db.session.commit()  # Lưu thay đổi vào cơ sở dữ liệu

        return True

    except NoResultFound:
        # Trường hợp không tìm thấy người dùng với ID đó
        return False

    except Exception as e:
        # Đảm bảo mọi lỗi khác đều được xử lý
        db.session.rollback()  # Quay lại trạng thái trước khi thực hiện thay đổi
        print(f"Error updating user: {e}")
        return False