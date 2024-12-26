
from saleapp import app, db, payment
from flask import render_template, request, redirect, session, flash, json, jsonify
from saleapp import admin, dao, login
from flask_login import login_user, logout_user, current_user, login_required, login_manager
from saleapp.decorators import annonymous_user
from sqlalchemy.orm import joinedload
from saleapp.models import Flight, Route, Flight_Class, Configuration,Ticket,Customer,Seat
from datetime import datetime
import cloudinary.uploader
from saleapp.models import UserRole, User


@app.route('/')
def index():
    if current_user.is_authenticated:
        username = current_user.id
    else:
        username = None
    session['username']=username
    return render_template('index.html')

@app.route('/history_ticket')
def history_ticket():
    username = session.get('username')
    tickets = Ticket.query.filter(Ticket.username == username).all()
    customer = None
    flight_1 = None
    flight_2 = None
    for ticket in tickets:
        customer = Customer.query.filter(Customer.ticket_id == ticket.id, Customer.email == ticket.email).all()
        if(customer):
            flight_id_1 = customer[0].flight_id_1
            flight_id_2 = customer[0].flight_id_2
            if(flight_id_1):
                flight_1=Flight.query.filter_by(id=flight_id_1).first()
                if (flight_id_2):
                    flight_2 = Flight.query.filter_by(id=flight_id_2).first()
                else:
                    flight_2=None

    return render_template('history_ticket.html',tickets=tickets,customer=customer,
                           flight_1=flight_1,flight_2=flight_2)


@app.route('/success', methods=['GET'])
@login_required
def success():
    user_email = session.get('user_email')
    total_price = session.get('amount')
    customer_name = session.get('customer_name')
    payment_status = request.args.get('status')
    type_class = session.get('type_class')
    type_class_2 = session.get('type_class_2')
    adult_info = session.get('adult_info')
    child_info = session.get('child_info')
    infant_info = session.get('infant_info')
    totalGuests = session.get('totalGuests')
    flight_id_1 = session.get('flight_id_1')
    flight_id_2 = session.get('flight_id_2')
    username = session.get('username')
    selected_seats = session.get('selected_seats')
    selected_seats1 = session.get('selected_seats1')
    ticket_id=dao.generate_id(Ticket,'OUA',4)
    flight1 = dao.lay_thong_tin_chuyen_bay_theo_id(flight_id_1)
    for i in range(len(selected_seats)):
        seat_id = dao.generate_id(Seat, 'SE', 4)
        dao.seat_infor(seat_id,flight_id_1,selected_seats[i])
    if (flight_id_2!=""):
        flight2 = dao.lay_thong_tin_chuyen_bay_theo_id(flight_id_2)
        for i in range(len(selected_seats1)):
            new_seat_id = dao.generate_id(Seat, 'SE', 4)
            dao.seat_infor(new_seat_id,flight_id_2,selected_seats1[i])
    else:
        flight_id_2 = None
        type_class_2 = None
        flight2 = None

    if payment_status == 'PAID':
        dao.send_payment_success_email(user_email, total_price, adult_info, child_info, infant_info)
        payment_date = session.get('date_time')
        payment_number = session.get('payment_number')
        payment_method = "Chuyển khoản"
        dao.payment_infor(payment_number,payment_method,total_price,payment_date)
        dao.ticket_infor(ticket_id,username,customer_name,totalGuests,total_price,payment_number,user_email)
        if (flight1):
            if (type_class == 'CLASS_1'):
                seat_count_class_1 = flight1.seat_count_class_1 - totalGuests
                flight1.seat_count_class_1 = seat_count_class_1
                flight1.seat_sell_class_1+=totalGuests
            else:
                seat_count_class_2 = flight1.seat_count_class_2 - totalGuests
                flight1.seat_count_class_2 = seat_count_class_2
                flight1.seat_sell_class_2+=totalGuests

        if (flight2):
            if (type_class == 'CLASS_1'):
                seat_count_class_12 = flight2.seat_count_class_1 - totalGuests
                flight2.seat_count_class_1 = seat_count_class_12
                flight2.seat_sell_class_1+=totalGuests

            else:
                seat_count_class_22 = flight2.seat_count_class_2 - totalGuests
                flight2.seat_count_class_2 = seat_count_class_22
                flight2.seat_sell_class_2+=totalGuests

        if adult_info:
            for info in adult_info:
                customer_id = dao.generate_id(Customer, 'CUS', 4)
                dao.customer_infor(customer_id,info['lastName'], info['fullName'], info['phone']
                                   , info['email'], info['cccd'], datetime.now(),username
                                   ,flight_id_1,type_class,flight_id_2,type_class_2,ticket_id)
        if child_info:
            for info in child_info:
                customer_id = dao.generate_id(Customer, 'CUS', 4)
                dao.customer_infor(customer_id,info['lastName'], info['fullName'], None
                                   , None, None, datetime.now(),username,
                                   flight_id_1,type_class,flight_id_2,type_class_2,ticket_id)

        if infant_info:
            for info in infant_info:
                customer_id = dao.generate_id(Customer, 'CUS', 4)
                dao.customer_infor(customer_id,info['lastName'], info['fullName'], None
                                   , None, None, datetime.now(),username,
                                   flight_id_1,type_class,flight_id_2,type_class_2,ticket_id)

    else:
        flash('Thanh toán không thành công, vui lòng thử lại.', 'danger')
    return render_template('success.html')


@app.route('/cancel')
def cancel():
    return render_template('cancel.html')


@app.route('/book_ticket')
@login_required
def book_ticket():
    sanbaydi = dao.get_all_departure_airports(db.session)
    sanbayden = dao.get_all_arrival_airports(db.session)
    return render_template('book_ticket.html', sanbaydi=sanbaydi, sanbayden=sanbayden)


@app.route('/search_flight', methods=['post', 'get'])
def search_flight():
    flight_class1 = Flight_Class.HANG_1
    flight_class2 = Flight_Class.HANG_2
    configurations = Configuration.query.all()  # Lấy tất cả các cấu hình
    config_dict = {}

    for config in configurations:
        config_dict['time_book_ticket'] = config.time_book_tickets

    if request.method.__eq__('POST'):
        diemdi = request.form['diemdi']
        diemden = request.form['diemden']
        ngaydi = request.form['ngaydi']
        ngayden = request.form['ngayden']
        tripType = request.form.get('tripType')
        session['tripType'] = tripType
        nguoilon = request.form['adultCount']
        treem = request.form['childCount']
        embe = request.form['infantCount']
        session['diemdi'] = diemdi
        session['diemden'] = diemden
        session['ngaydi'] = ngaydi
        session['ngayden'] = ngayden
        session['adult'] = nguoilon
        session['child'] = treem
        session['infant'] = embe

        kq = dao.tim_tuyen_bay_theo_diem(diemdi, diemden, ngaydi)
        kq1 = None
        if ngayden != "":
            kq1 = dao.ngay_ve(diemdi, diemden, ngayden)

    return render_template('search_flight.html', kq=kq, kq1=kq1, configurations=configurations,
                           config_dict=config_dict,
                           flight_class1=flight_class1, flight_class2=flight_class2, tripType=tripType,
                           nguoilon=nguoilon, treem=treem, embe=embe)


@app.route('/flight_infor', methods=['post', 'get'])
@login_required
def flight_infor():
    if request.method.__eq__('POST'):
        flight_id_1 = request.form.get('flight_id_1')
        session['flight_id_1'] = flight_id_1
        route_name_1 = request.form.get('route_name_1')
        session['route_name_1'] = route_name_1
        departure_time_1 = request.form['departure_time_1']
        arrival_time_1 = request.form['arrival_time_1']
        arrival_time_2 = request.form['arrival_time_2']
        type_class = request.form.get('type_Class_1')
        session['type_class'] = type_class
        flight_id_2 = request.form.get('flight_id_2')
        session['flight_id_2'] = flight_id_2
        route_name_2 = request.form.get('route_name_2')
        session['route_name_2'] = route_name_2
        departure_time_2 = request.form['departure_time_2']
        type_class_2 = request.form.get('type_Class_2')
        session['type_class_2'] = type_class_2
        nguoilon = int(session.get('adult'))
        treem = int(session.get('child'))
        embe = int(session.get('infant'))
        ticket_price_class_1 = request.form['seat_price_class_1']
        ticket_price_class_2 = request.form['seat_price_class_2']
        seat_flight_1 = Seat.query.filter(Seat.flight_id==flight_id_1)
        booked_seat_ids = [seat.seat_number for seat in seat_flight_1]

        booked_seat_ids1=None
        if(flight_id_2!=""):
            seat_flight_2 = Seat.query.filter(Seat.flight_id==flight_id_2)
            booked_seat_ids1 = [seat.seat_number for seat in seat_flight_2]

    return render_template('flight_infor.html', route_name_1=route_name_1, departure_time_1=departure_time_1,
                           arrival_time_1=arrival_time_1, arrival_time_2=arrival_time_2,
                           type_class=type_class, route_name_2=route_name_2, departure_time_2=departure_time_2,
                           type_class_2=type_class_2,
                           ticket_price_class_1=ticket_price_class_1,
                           ticket_price_class_2=ticket_price_class_2,
                           nguoilon=nguoilon, treem=treem, embe=embe,

                           booked_seat_ids=booked_seat_ids,booked_seat_ids1=booked_seat_ids1)


@app.route('/login-admin', methods=['post'])
def admin_login():
    username = request.form['username']
    password = request.form['password']
    user = dao.auth_user(username=username, password=password)

    if user and (user.user_role == UserRole.ADMIN or user.user_role == UserRole.USER):
        login_user(user=user)
        flash('Đăng nhập thành công!', 'success')
    else:
        flash('Tên đăng nhập hoặc mật khẩu không đúng', 'error')
    return redirect('/admin')


@app.route('/register', methods=['get', 'post'])
def register():
    err_msg = ''
    err_username=''
    err_email=''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        usernames = User.query.filter(User.username == username)
        emails=User.query.filter(User.email == request.form['email'])
        if(usernames):
            err_username = "Tên đăng nhập đã tồn tại"
        if(emails):
            err_email = "Email bạn nhập đã tồn tại"
        if password.__eq__(confirm):
            avatar = ''
            if request.files:
                res = cloudinary.uploader.upload(request.files['avatar'])
                avatar = res['secure_url']
            try:
                dao.register(name=request.form['name'],
                             username=request.form['username'],
                             password=password,
                             email=request.form['email'],
                             avatar=avatar)
                return redirect('/login')
            except:
                err_msg = 'Lỗi'
        else:
            err_msg = 'Mật khẩu không khớp'

    return render_template('register.html', err_msg=err_msg,err_username=err_username,
                           err_email=err_email)


@app.route('/login', methods=['get', 'post'])
@annonymous_user
def user_login():
    err_msg1 = ''
    if request.method.__eq__('POST'):
        username = request.form['username']
        password = request.form['password']
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect('/')
        else:
            err_msg1 = 'Tên đăng nhập hoặc mật khẩu không đúng'
    return render_template('login.html', err_msg1=err_msg1)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/logout-admin')
@login_required
def logout_admin():
    logout_user()
    return redirect('/admin')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route('/create_payment_link', methods=['POST', 'GET'])
@login_required
def handle_create_payment_link():
    if request.method.__eq__('POST'):
        amount_str = request.form['total-prices']
        user_email1 = request.form.get('emailAdult0')
        customer_name = request.form.get('lastNameAdult0')+ " " + request.form.get('fullNameAdult0')
        session['customer_name'] = customer_name
        session['user_email'] = user_email1
        amount = int(amount_str.replace('.', '').replace(',', ''))
        session['amount'] = amount
        totalGuests = int(session.get('adult')) + int(session.get('child')) + int(session.get('infant'))
        session['totalGuests'] = totalGuests
        selected_seats = request.form.get('selectedSeats')
        selected_seats1 = request.form.get('selectedSeats1')

        if selected_seats:
            selected_seats = json.loads(selected_seats)
        else:
            selected_seats = []
        session['selected_seats'] = selected_seats

        if selected_seats1:
            selected_seats1 = json.loads(selected_seats1)
        else:
            selected_seats1 = []
        session['selected_seats1'] = selected_seats1
    if int(session.get('adult')) > 0:
        adult_info = []
        for i in range(int(session.get('adult'))):
            lastName = request.form.get(f'lastNameAdult{i}')
            fullName = request.form.get(f'fullNameAdult{i}')
            dob = request.form.get(f'dobAdult{i}')
            email = request.form.get(f'emailAdult{i}')
            phone = request.form.get(f'phoneAdult{i}')
            cccd = request.form.get(f'cccdAdult{i}')

            adult_info.append({
                'lastName': lastName,
                'fullName': fullName,
                'dob': dob,
                'email': email,
                'phone': phone,
                'cccd': cccd
            })
        session['adult_info'] = adult_info

    if int(session.get('child')) > 0:
        child_info = []
        for i in range(int(session.get('child'))):
            lastName = request.form.get(f'lastNameChild{i}')
            fullName = request.form.get(f'fullNameChild{i}')
            dob = request.form.get(f'dobChild{i}')

            child_info.append({
                f'Thông tin khách hàng thứ {i + 1} : '
                'lastName': lastName,
                'fullName': fullName,
                'dob': dob,
            })
        session['child_info'] = child_info
    if int(session.get('infant')) > 0:
        infant_info = []
        for i in range(int(session.get('infant'))):
            infant_info.append({
                'lastName': request.form.get(f'lastNameInfant{i}'),
                'fullName': request.form.get(f'fullNameInfant{i}'),
                'dob': request.form.get(f'dobInfant{i}')
            })
        session['infant_info'] = infant_info
    payment_response = payment.create_payment(amount)
    return jsonify(payment_response)


@app.route('/infor_user')
def infor_user():
 if current_user.is_authenticated:
    infor_user = current_user.id
    kq=dao.get_user_by_id(infor_user)
    id_user = request.args.get('id_user')
    name_user = request.args.get('name_user')
    username_user = request.args.get('username_user')
    email = request.args.get('email_user')
    phone_user=request.args.get('phone_number')
    kq1=dao.update_user_name_by_id(id_user,name_user,username_user,email,phone_user)
    return render_template ('infor_user.html',kq1=kq1, kq=kq, id_user=id_user, name_user=name_user,email=email,phone_user=phone_user)

if __name__ == '__main__':
    app.run(debug=True)

