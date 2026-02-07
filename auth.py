import bcrypt
from db import get_connection
from datetime import datetime

def create_users_table():
    """Create users table if it doesn't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP NULL,
        INDEX idx_email (email)
    )
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
    print("Users table created successfully!")

def hash_password(password):
    """Hash a password using bcrypt"""
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_user(email, password, full_name, role):
    """Create a new user in the database"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Hash the password
        password_hash = hash_password(password)
        
        # Insert user
        insert_query = """
        INSERT INTO users (email, password_hash, full_name, role)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (email, password_hash, full_name, role))
        conn.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return {"success": True, "user_id": user_id}
    
    except Exception as e:
        print(f"Error creating user: {e}")
        return {"success": False, "error": str(e)}

def authenticate_user(email, password):
    """Authenticate a user by email and password"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user by email
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return {"success": False, "error": "Invalid email or password"}
        
        # Verify password
        if verify_password(password, user['password_hash']):
            # Update last login
            update_query = "UPDATE users SET last_login = %s WHERE id = %s"
            cursor.execute(update_query, (datetime.now(), user['id']))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "role": user['role']
                }
            }
        else:
            cursor.close()
            conn.close()
            return {"success": False, "error": "Invalid email or password"}
    
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return {"success": False, "error": str(e)}

def get_user_by_email(email):
    """Get user information by email"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT id, email, full_name, role, created_at FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return user
    
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

# Initialize database table when module is imported
if __name__ == "__main__":
    create_users_table()
    print("Authentication system initialized!")
