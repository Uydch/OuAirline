from saleapp.models import User, UserRole, Flight, Airport, Route, Ticket, Configuration,Customer
from saleapp import db,app,dao
from saleapp.models import Flight_Class
from flask_admin import Admin,BaseView,expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from datetime import timedelta,datetime
from markupsafe import Markup
from flask import redirect,request,flash,url_for,session
from wtforms import ValidationError

admin=Admin(app=app,name='Quản lý chuyến bay',template_mode='bootstrap4')


class AdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class UserBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.USER

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class UserModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.USER

class AdminUserModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.user_role == UserRole.USER or current_user.user_role == UserRole.ADMIN  )


class StatsView(AdminBaseView):
    @expose('/')
    def __index__(self):
        kq = dao.count_flight_by_route()
        route_name = request.args.get('kw')
        month = request.args.get('month')
        year = request.args.get('year')
        kq1 = dao.tinh_tong_tien_theo_tuyen_bay(month, year, route_name)
        tong_doanh_thu_1 = sum(item[2] for item in kq1)
        # ---------------------------
        month1 = request.args.get('month1')
        year1 = request.args.get('year1')
        route_name_1 = request.args.get('kw1')
        kq2 = dao.tinh_tong_tien_theo_tuyen_bay(month1, year1, route_name_1)
        tong_doanh_thu_2 = sum(item[2] for item in kq2)
        revenue_ratios = [round((item[2] / tong_doanh_thu_2) * 100, 2) for item in kq2]  # Trả về 1 list
        # -----------
        month2 = request.args.get('month2')
        year2 = request.args.get('year2')
        route_name_2 = request.args.get('kw2')
        kq3 = dao.count_turn_flight_by_route(month2, year2, route_name_2)
        tong_so_luot = sum(item[2] for item in kq3)
        return self.render('admin/stats.html', kq=kq, kq1=kq1, month=month, year=year, kq2=kq2,
                           tong_doanh_thu_1=tong_doanh_thu_1, tong_doanh_thu_2=tong_doanh_thu_2,
                           revenue_ratios=revenue_ratios
                           , month1=month1, year1=year1, month2=month2, year2=year2, kq3=kq3,
                           tong_so_luot=tong_so_luot, route_name_1=route_name_1, route_name=route_name,
                           route_name_2=route_name_2)


class UserView(AdminModelView):
    column_exclude_list = ['avatar','password']
    column_labels = {
        'username': 'Tên tài khoản',
        'name': 'Họ và tên',
        'user_role': 'chức vụ '
    }


class FlightModelView(AdminUserModelView):
    form_columns = ('departure_time', 'arrival_time','route','seat_count_class_1','seat_price_class_1','seat_count_class_2','seat_price_class_2','airports','flight_status',)
    column_searchable_list = ['departure_time','route.name','route.departure_airport.name',]
    column_list = ['id','departure_time','route','route.departure_airport.name','route.arrival_airport.name','seat_count_class_1','seat_price_class_1','seat_sell_class_1','seat_count_class_2','seat_price_class_2','seat_sell_class_2','airports','flight_status_display','seats']
    column_labels = {
        'id': 'Số hiệu ',
        'route':'Tuyến bay',
        'seat_count_class_1': 'Số lượng ghế hạng 1',
        'seat_count_class_2': 'Số lượng ghế hạng 2',
        'departure_time':'Thời gian khởi hành',
        'arrival_time':'Thời gian đến',
        'airports':'Sân bay trung gian',
        'flight_status':'Trạng thái',
        'rout.name':'tuyến bay',
        'route.departure_airport.name':'Sân bay đi',
        'route.arrival_airport.name':'Sân bay đến',
        'flight_status_display':'Trạng thái',
        'seat_sell_class_1':'Số ghế hạng 1 đã bán',
        'seat_sell_class_2':'Số ghế hạng 2 đã bán',
        'seat_price_class_1':'Gía hạng 1',
        'seat_price_class_2':'Gía hạng 2'

    }

    def on_model_change(self, form, model, is_created):
        config = Configuration.query.first()
        if config and len(form.airports.data) > config.max_stopover_airports:
            raise ValidationError(f"Bạn chỉ có thể chọn tối đa {config.max_stopover_airports} sân bay trung gian.")


        if (model.arrival_time - model.departure_time) < timedelta(minutes=config.min_flight_time):
            raise ValidationError("Thời gian bay phải tối thiểu 30 phút.")

        return super(FlightModelView, self).on_model_change(form, model, is_created)


class RouteModelView(AdminModelView):
    column_list = ('id','name', 'departure_airport','arrival_airport','flights')
    form_columns = ('departure_airport','arrival_airport')
    column_labels = {
        'id': 'Mã tuyến bay',
        'name': 'Tên tuyến bay',
        'departure_airport': 'Sân bay đi ',
        'arrival_airport': 'Sân bay đến',
        'flights':'Thông tin chuyến bay'
    }

    def _list_flights(view, context, model, name):
        flights = model.flights
        return Markup(
            '<br>'.join([str(flight) for flight in flights]))
    column_formatters = {
        'flights': _list_flights
    }

    def on_model_change(self, form, model, is_created):
        if model.departure_airport.id == model.arrival_airport.id:
            raise ValidationError("Sân bay đi và sân bay đến không thể trùng nhau!")
        return super().on_model_change(form, model, is_created)


class AirportModelView(AdminModelView):
    column_list = ('id', 'name', 'city', 'country')
    form_columns = ('id', 'name', 'city', 'country')
    column_labels = {
        'id': 'Mã sân bay',
        'name': 'Tên sân bay',
        'city': 'Thành Phố ',
        'country':'Quốc Gia'
    }
    def on_model_change(self, form, model, is_created):
        config = Configuration.query.first()
        if Airport.query.count() - 1 >= config.num_airports:
            raise ValidationError(f"Số lượng sân bay đã đạt giới hạn là {config.num_airports}. Vui lòng chỉnh sửa trong mục thay đổi quy định!")
        return super().on_model_change(form, model, is_created)


class FlightScheduleModelView(AdminModelView):
    pass


class TicketModelView(UserModelView):
    can_export = True


class ConfigurationModelView(AdminModelView):
    column_labels = {
        'num_airports': 'Số lượng sân bay tối đa',
        'min_flight_time': 'Thời gian bay tối thiểu',
        'max_stopover_airports': 'Số sân bay trung gian tối đa',
        'min_stopover_time':'Thời gian dừng tối thiểu ',
        'max_stopover_time':'Thời gian dừng tối đa',
        'num_ticket_classes' : 'Số lượng hạng vé',
        'time_book_tickets':'Thời gian đặt vé',
        'time_sell_tickets':"Thời gian bán vé"

    }
    can_create = False


class LogoutView(BaseView):
    def is_accessible(self):
         return current_user.is_authenticated
    @expose('/')
    def index(self):
        return redirect('/logout-admin')


class TicketSaleView(UserBaseView):
    @expose('/',methods=['get','post'])
    def index(self):
        flights = Flight.query.all()  # Lấy danh sách chuyến bay
        sanbaydi = dao.get_all_departure_airports(db.session)
        sanbayden = dao.get_all_arrival_airports(db.session)
        return self.render('admin/ticket_sale.html', flights=flights, sanbaydi=sanbaydi, sanbayden=sanbayden)

    @expose('/search_flight', methods=['post', 'get'])
    def search_flight(self):
        if request.method.__eq__('POST'):
            diemdi = request.form['diemdi']
            diemden = request.form['diemden']
            ngaydi = request.form['ngaydi']
            ngayden = request.form['ngayden']
            tripType = request.form['tripType']
            nguoilon = request.form.get('adultCount')
            treem = request.form.get('childCount')
            embe = request.form.get('infantCount')
            session['adult'] = nguoilon
            session['child'] = treem
            session['infant'] = embe

            kq = dao.tim_tuyen_bay_theo_diem(diemdi, diemden, ngaydi)
            kq1 = None
            if ngayden != "":
                kq1 = dao.ngay_ve(diemdi, diemden, ngayden)

            flight_class1 = Flight_Class.HANG_1
            flight_class2 = Flight_Class.HANG_2

            configurations = Configuration.query.all()  # Lấy tất cả các cấu hình
            config_dict = {}

            for config in configurations:
                config_dict['time_sell_ticket'] = config.time_sell_tickets

            return self.render('admin/search_flight.html',kq=kq, kq1=kq1, configurations=configurations,config_dict=config_dict,
                                       flight_class1=flight_class1, flight_class2=flight_class2, tripType=tripType,
                                       nguoilon=nguoilon, treem=treem, embe=embe)


    @expose('/search_flight/flight_info', methods=['post', 'get'])
    def flight_info(self):
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
            ticket_price_class_1 = request.form['ticket_price_class_1']
            ticket_price_class_2 = request.form['ticket_price_class_2']

        return self.render('admin/flight_info.html', route_name_1=route_name_1, departure_time_1=departure_time_1,
                               arrival_time_1=arrival_time_1, arrival_time_2=arrival_time_2,
                               type_class=type_class, route_name_2=route_name_2, departure_time_2=departure_time_2,
                               type_class_2=type_class_2,
                               ticket_price_class_1=ticket_price_class_1,
                               ticket_price_class_2=ticket_price_class_2,
                               nguoilon=nguoilon, treem=treem, embe=embe)

    @expose('/search_flight/flight_info/sendmail', methods=['post', 'get'])
    def send_mail(self):
        if request.method.__eq__('POST'):
            amount_str = request.form.get('total-prices')
            user_email1 = request.form.get('emailAdult0')
            session['user_email'] = user_email1
            amount = int(amount_str.replace('.', '').replace(',', ''))
            session['amount'] = amount
            type_class = session.get('type_class')
            type_class_2 = session.get('type_class_2')
            totalGuests = int(session.get('adult'))+int(session.get('child'))+int(session.get('infant'))
            flight_id_1 = session.get('flight_id_1')
            flight_id_2 = session.get('flight_id_2')
            username = current_user.id
            customer_name = request.form.get('lastNameAdult0') + " " + request.form.get('fullNameAdult0')
            customer_id = dao.generate_id(Customer, 'CUS', 4)
            ticket_id = dao.generate_id(Ticket, 'OUA', 4)
            flight1 = dao.lay_thong_tin_chuyen_bay_theo_id(flight_id_1)
            if (flight_id_2 != ""):
                flight2 = dao.lay_thong_tin_chuyen_bay_theo_id(flight_id_2)
            else:
                flight_id_2 = None
                type_class_2 = None
                flight2 = None

        adult_info = []
        if int(session.get('adult')) > 0:
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

        child_info = None
        if int(session.get('child')) > 0:
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

        infant_info = []
        if int(session.get('infant')) > 0:
            for i in range(int(session.get('infant'))):
                infant_info.append({
                    'lastName': request.form.get(f'lastNameInfant{i}'),
                    'fullName': request.form.get(f'fullNameInfant{i}'),
                    'dob': request.form.get(f'dobInfant{i}')
                })

        if user_email1:
            dao.send_payment_success_email(user_email1, amount, adult_info, child_info, infant_info)
            payment_date = session.get('date_time')
            payment_number = session.get('payment_number')
            payment_method = "Chuyển khoản"
            dao.payment_infor(payment_number, payment_method, amount, payment_date)
            dao.ticket_infor(ticket_id, username, customer_name, totalGuests, amount, payment_number, user_email1)
            if (flight1):
                if (type_class == 'CLASS_1'):
                    seat_count_class_1 = flight1.seat_count_class_1 - totalGuests
                    flight1.seat_count_class_1 = seat_count_class_1
                else:
                    seat_count_class_2 = flight1.seat_count_class_2 - totalGuests
                    flight1.seat_count_class_2 = seat_count_class_2
            if (flight2):
                if (type_class == 'CLASS_1'):
                    seat_count_class_12 = flight2.seat_count_class_1 - totalGuests
                    flight2.seat_count_class_1 = seat_count_class_12
                else:
                    seat_count_class_22 = flight2.seat_count_class_2 - totalGuests
                    flight2.seat_count_class_2 = seat_count_class_22
        if adult_info:
            for info in adult_info:
                dao.customer_infor(customer_id, info['lastName'], info['fullName'], info['phone']
                                   , info['email'], info['cccd'], datetime.now(), username
                                   , flight_id_1, type_class, flight_id_2, type_class_2, ticket_id)

        if child_info:
            for info in child_info:
                dao.customer_infor(customer_id, info['lastName'], info['fullName'], None
                                   , None, None, datetime.now(), username,
                                   flight_id_1, type_class, flight_id_2, type_class_2, ticket_id)

        if infant_info:
            for info in infant_info:
                dao.customer_infor(customer_id, info['lastName'], info['fullName'], None
                                   , None, None, datetime.now(), username,
                                   flight_id_1, type_class, flight_id_2, type_class_2, ticket_id)
        return self.render('admin/success.html')



admin.add_view(TicketSaleView(name='Bán vé'))
admin.add_view(FlightModelView(Flight,db.session,name='Chuyến Bay'))
admin.add_view(RouteModelView(Route,db.session,name='Tuyến bay'))
admin.add_view(AirportModelView(Airport,db.session,name='Sân Bay'))
admin.add_view(TicketModelView(Ticket,db.session,name='Vé'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(UserView(User, db.session,name='Người dùng'))
admin.add_view(ConfigurationModelView(Configuration,db.session,name='Thay đổi quy định'))
admin.add_view(LogoutView(name='Đăng xuất'))