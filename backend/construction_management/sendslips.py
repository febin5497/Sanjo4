# send_slips.py

from flask import Flask
from flask_mail import Message
from datetime import datetime, timedelta
from xhtml2pdf import pisa
from io import BytesIO
from mail import mail
from config import Config
from attendance_management.models import Attendance
from staff_management.models import Staff, db
from routes import render_salary_html, calculate_salary_slip

app = Flask(__name__)
app.config.from_object(Config)
mail.init_app(app)
db.init_app(app)

def send_salary_slips():
    with app.app_context():
        today = datetime.today()
        first_day = today.replace(day=1)
        last_month = first_day - timedelta(days=1)
        month = last_month.month
        year = last_month.year

        staff_list = Staff.query.all()
        for staff in staff_list:
            attendances = Attendance.query.filter(
                Attendance.staff_id == staff.id,
                db.extract('month', Attendance.date) == month,
                db.extract('year', Attendance.date) == year
            ).all()

            if not attendances or not staff.email:
                continue

            result = calculate_salary_slip(staff, attendances, month, year)
            html = render_salary_html(result, "http://localhost:5000/")  # or your base domain

            pdf = BytesIO()
            pisa.CreatePDF(src=html, dest=pdf)
            pdf.seek(0)

            msg = Message(
                subject=f"Your Salary Slip for {datetime(year, month, 1).strftime('%B %Y')}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[result["email"]],
                html=html
            )
            msg.attach(f"Salary_Slip_{staff.id}_{month}_{year}.pdf", "application/pdf", pdf.read())

            try:
                mail.send(msg)
                print(f"✅ Sent to {result['email']}")
            except Exception as e:
                print(f"❌ Error sending to {result['email']}: {e}")

if __name__ == "__main__":
    send_salary_slips()
