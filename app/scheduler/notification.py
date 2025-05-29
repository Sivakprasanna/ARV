from app.db import get_db_connection

def get_pending_dose_reminders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT 
        p.name AS patient_name,
        p.mobile,
        p.patient_id,
        ds.dose_number,
        ds.scheduled_date,
        e.exposure_type,
        e.bite_date
    FROM 
        dose_schedule ds
    JOIN exposures e ON ds.exposure_id = e.id
    JOIN patients p ON e.patient_id = p.id
    WHERE 
        ds.status = 'pending'
        AND ds.scheduled_date IN (CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 DAY));
    """

    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
