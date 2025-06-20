from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_db_connection
from datetime import datetime, timedelta
import random
import string

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

# Utility to generate unique patient_id
def generate_patient_id():
    return 'RAB' + ''.join(random.choices(string.digits, k=4))

@patient_bp.route('/register', methods=['GET', 'POST'])
def register_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        mobile = request.form['mobile']
        address = request.form['address']
        bite_type = request.form['bite_type']
        bite_date = request.form['bite_date']
        category = request.form['bite_category']

        patient_id = generate_patient_id()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Insert into patients table
            cursor.execute("""
                INSERT INTO patients (name, age, sex, mobile, patient_id, address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, age, sex, mobile, patient_id, address))
            patient_db_id = cursor.lastrowid

            # Insert into exposures table
            cursor.execute("""
                INSERT INTO exposures (patient_id, exposure_type, bite_date, category)
                VALUES (%s, %s, %s, %s)
            """, (patient_db_id, bite_type.lower(), bite_date, category))
            exposure_id = cursor.lastrowid

            # Calculate and insert dose_schedule based on exposure type
            today = datetime.today()


            if bite_type.lower() == 'new':
                # Skip Day 0, schedule Day 3, 7, 28
                dose_days = [3, 7, 28]
            elif bite_type.lower() == 're-exposure':
                # Only Day 3 is required
                dose_days = [3]
            else:
                dose_days = []

            for i, d in enumerate(dose_days):
                scheduled = today + timedelta(days=d)
                cursor.execute("""
                    INSERT INTO dose_schedule (exposure_id, dose_number, scheduled_date)
                    VALUES (%s, %s, %s)
                """, (exposure_id, i + 1, scheduled.date()))

            dose_schedule = [(i + 1, (today + timedelta(days=d)).strftime('%Y-%m-%d')) for i, d in enumerate(dose_days)]


            return render_template('success.html',
                                   name=name,
                                   patient_id=patient_id,
                                   dose_schedule=dose_schedule)

            flash('Patient registered successfully with ARV schedule!', 'success')

        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'error')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('patient.register_patient'))

    return render_template('register_patient.html')

@patient_bp.route('/home')
def home():
    return render_template('home.html')
