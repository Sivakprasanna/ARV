from flask import Blueprint, render_template, flash, redirect
from app.db import get_db_connection
from flask import request
from datetime import date

general_bp = Blueprint('general', __name__)

@general_bp.route('/patients/view')
def view_patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
    SELECT p.*,
        CASE
            WHEN EXISTS (
                SELECT 1 FROM dose_schedule ds
                JOIN exposures e ON ds.exposure_id = e.id
                WHERE e.patient_id = p.id AND ds.status = 'pending'
            ) THEN 'pending'
            WHEN EXISTS (
                SELECT 1 FROM dose_schedule ds
                JOIN exposures e ON ds.exposure_id = e.id
                WHERE e.patient_id = p.id AND ds.status = 'missed'
            ) THEN 'missed'
            ELSE 'completed'
        END AS dose_status,
        EXISTS (
            SELECT 1 FROM dose_schedule ds
            JOIN exposures e ON ds.exposure_id = e.id
            WHERE e.patient_id = p.id
              AND ds.scheduled_date = CURDATE()
        ) AS has_today_dose
    FROM patients p
""")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('patientview.html', patients=patients)


@general_bp.route('/patients/<int:patient_id>')
def patient_detail(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get patient details
    cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = cursor.fetchone()

    if not patient:
        cursor.close()
        conn.close()
        return "Patient not found", 404

    # Get exposure id(s)
    cursor.execute("SELECT * FROM exposures WHERE patient_id = %s", (patient_id,))
    exposures = cursor.fetchall()

    dose_schedules = []
    for exposure in exposures:
        cursor.execute("""
            SELECT id, dose_number, scheduled_date, actual_date, status
            FROM dose_schedule
            WHERE exposure_id = %s
            ORDER BY dose_number
        """, (exposure['id'],))
        doses = cursor.fetchall()
        dose_schedules.append({
            'exposure_type': exposure['exposure_type'],
            'bite_date': exposure['bite_date'],
            'category': exposure['category'],
            'doses': doses
        })

    cursor.close()
    conn.close()
    print("Patient:", patient)
    print("Dose Schedules:", dose_schedules)
    print("Current Date:", date.today())
    return render_template('patient_detail.html', patient=patient,dose_schedules=dose_schedules,current_date=date.today())


@general_bp.route('/dose/<int:dose_id>/update', methods=['POST'])
def update_dose(dose_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE dose_schedule
            SET actual_date = %s, status = 'given'
            WHERE id = %s
        """, (date.today(), dose_id))
        conn.commit()
        flash("Dose marked as given.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error updating dose: {e}", "error")
    finally:
        cursor.close()
        conn.close()

    # Redirect back to the referring patient page
    return redirect(request.referrer)
