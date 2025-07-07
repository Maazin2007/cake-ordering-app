import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import EmailNotValidError, validate_email
from flask import session, redirect, url_for, flash
from functools import wraps

# function to check if the user email is valid
def checkmail(mail):
    try:
        # Validate the email format and domain
        validate_email(mail)
        return True
    except EmailNotValidError as e:
        return False

# function to check if the mail is already registered
def check_mail_exists(mail):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                    SELECT *  FROM people WHERE mail = ?
                   """, (mail,))
    rows = cursor.fetchall()
      
    cursor.close()
    conn.close()
    
    return len(rows) > 0
    
    
# function to help with sql
def get_db():
    conn = sqlite3.connect("bakery.db")
    conn.row_factory = sqlite3.Row
    return conn

# function to add new user to the database
def add_new_user(name, mail, hash):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                   INSERT INTO people (mail, hash, name) VALUES (?, ?, ?)
                   """, (mail, hash, name,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
def user_id_by_mail(mail):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT id FROM people WHERE mail = ?
                   """, (mail,))
    row = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if row:
        return row["id"]
    else:
        return None
    

# function to check if mail and password match
def check_password(mail, password):
    # convert password to hash
    input_password_hash = generate_password_hash(password)
    
    # get hash stored inside the database
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT hash FROM people WHERE mail = ?
                   """, (mail, ))
    row = cursor.fetchone()
    
    if row is None:
        return False
    
    stored_hash = row["hash"]
    return check_password_hash(stored_hash, password)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))  # Redirect to login page if not logged in
        return f(*args, **kwargs)  # Proceed with the original view function
    return decorated_function


# check if the user is a admin or not 
def check_admin(id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT is_admin FROM people 
                   WHERE id = ?
                   """, (id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return False
    
    return row["is_admin"] == 1

# function to get all the cakes from the database
def get_items():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT * FROM items
                   """)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return rows
        