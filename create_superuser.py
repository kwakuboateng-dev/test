from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from models import User
from auth import get_password_hash
import sys

def create_superuser():
    db = SessionLocal()
    try:
        print("Create a Superuser")
        email = input("Email: ")
        username = input("Username (anonymous_handle): ")
        password = input("Password: ")
        
        # Check if user exists
        existing_user = db.query(User).filter((User.email == email) | (User.anonymous_handle == username)).first()
        if existing_user:
            print("Error: User with this email or username already exists.")
            return

        hashed_password = get_password_hash(password)
        
        superuser = User(
            email=email,
            anonymous_handle=username,
            hashed_password=hashed_password,
            is_superuser=True,
            verified=True,
            real_name="Super Admin"
        )
        
        db.add(superuser)
        db.commit()
        print(f"✅ Superuser {username} created successfully!")
        
    except Exception as e:
        print(f"Error creating superuser: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()
