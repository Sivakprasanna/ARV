from flask import Blueprint, jsonify, request, render_template
from datetime import datetime, timedelta
import calendar
from app.db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')  # Ensure this file exists in your templates folder

def get_month_start_end(year, month):
    start_date = datetime(year, month, 1).date()
    last_day = calendar.monthrange(year, month)[1]
    end_date = datetime(year, month, last_day).date()
    return start_date, end_date

@dashboard_bp.route('/dashboard-data')
def dashboard_data():
    try:
        offset = int(request.args.get('offset', 0))
        today = datetime.today()
        target_month = today.month - offset
        target_year = today.year

        # Handle month overflow
        while target_month < 1:
            target_month += 12
            target_year -= 1
        while target_month > 12:
            target_month -= 12
            target_year += 1

        start_date, end_date = get_month_start_end(target_year, target_month)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # --- Current Month Stats ---
        # Total rabies cases
        cursor.execute("""
            SELECT COUNT(*) AS case_count 
            FROM exposures 
            WHERE bite_date BETWEEN %s AND %s
        """, (start_date, end_date))
        case_count = cursor.fetchone()['case_count']

        # Total doses scheduled
        cursor.execute("""
            SELECT COUNT(*) AS total_doses
            FROM dose_schedule 
            WHERE scheduled_date BETWEEN %s AND %s
        """, (start_date, end_date))
        total_doses = cursor.fetchone()['total_doses']

        # Completed doses
        cursor.execute("""
            SELECT COUNT(*) AS completed_doses
            FROM dose_schedule 
            WHERE status = 'given' AND actual_date BETWEEN %s AND %s
        """, (start_date, end_date))
        completed_doses = cursor.fetchone()['completed_doses']

        # Missed doses
        cursor.execute("""
            SELECT COUNT(*) AS missed_doses
            FROM dose_schedule 
            WHERE status = 'missed' AND scheduled_date BETWEEN %s AND %s
        """, (start_date, end_date))
        missed_doses = cursor.fetchone()['missed_doses']

        stats = {
            "case_count": case_count,
            "total_doses": total_doses,
            "completed_doses": completed_doses,
            "missed_doses": missed_doses
        }

        # --- Bar Chart Data for Last 3 Months ---
        chart_labels = []
        total_doses_list = []
        completed_doses_list = []
        missed_doses_list = []

        for i in range(2, -1, -1):  # 2 months before to current
            month = today.month - offset - i
            year = today.year

            while month < 1:
                month += 12
                year -= 1

            label = calendar.month_name[month]
            chart_labels.append(label)

            s_date, e_date = get_month_start_end(year, month)

            # total
            cursor.execute("SELECT COUNT(*) AS count FROM dose_schedule WHERE scheduled_date BETWEEN %s AND %s", (s_date, e_date))
            total_doses_list.append(cursor.fetchone()['count'])

            # completed
            cursor.execute("SELECT COUNT(*) AS count FROM dose_schedule WHERE status='given' AND actual_date BETWEEN %s AND %s", (s_date, e_date))
            completed_doses_list.append(cursor.fetchone()['count'])

            # missed
            cursor.execute("SELECT COUNT(*) AS count FROM dose_schedule WHERE status='missed' AND scheduled_date BETWEEN %s AND %s", (s_date, e_date))
            missed_doses_list.append(cursor.fetchone()['count'])

        chart = {
            "labels": chart_labels,
            "total_doses": total_doses_list,
            "completed_doses": completed_doses_list,
            "missed_doses": missed_doses_list
        }

        cursor.close()
        conn.close()

        return jsonify({"stats": stats, "chart": chart})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
