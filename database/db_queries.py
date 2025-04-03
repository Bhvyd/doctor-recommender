from db_connections import get_db_connection


def get_nearby_doctors(latitude, longitude, max_distance):
    query = """
    SELECT d.name, d.degree, d.years_experience, d.fee, s.speciality, l.locality_name,
           (6371 * acos(cos(radians(%s)) * cos(radians(d.latitude)) 
           * cos(radians(d.longitude) - radians(%s)) 
           + sin(radians(%s)) * sin(radians(d.latitude)))) AS distance
    FROM doctor_info d
    JOIN doc_speciality ds ON d.id = ds.doctor_id
    JOIN speciality s ON ds.speciality_id = s.id
    JOIN locality l ON d.locality_id = l.id
    HAVING distance < %s
    ORDER BY distance;
    """
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(query, (latitude, longitude, latitude, max_distance))
        results = cursor.fetchall()
    connection.close()
    return results


def get_nearby_doctors_by_speciality(latitude, longitude, speciality, max_distance):
    query = """
    SELECT d.name, d.degree, d.years_experience, d.fee, s.speciality, l.locality_name,
           (6371 * acos(cos(radians(%s)) * cos(radians(d.latitude)) 
           * cos(radians(d.longitude) - radians(%s)) 
           + sin(radians(%s)) * sin(radians(d.latitude)))) AS distance
    FROM doctor_info d
    JOIN doc_speciality ds ON d.id = ds.doctor_id
    JOIN speciality s ON ds.speciality_id = s.id
    JOIN locality l ON d.locality_id = l.id
    WHERE s.speciality = %s
    HAVING distance < %s
    ORDER BY distance;
    """
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(query, (latitude, longitude, latitude, speciality, max_distance))
        results = cursor.fetchall()
    connection.close()
    return results
