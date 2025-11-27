# Odoyewu - Setup Guide

## Backend Setup (FastAPI)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Database
Update `database.py` with your PostgreSQL credentials:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/odoyewu"
```

### 3. Create Database Tables
```bash
# In Python shell
python
>>> from database import engine, Base
>>> from models import User, Match, Message, Mission
>>> Base.metadata.create_all(bind=engine)
>>> exit()
```

### 4. Run the Server
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

---

## Frontend Setup (Expo)

### 1. Install Dependencies
```bash
cd mobile
npm install expo-blur expo-linear-gradient axios
```

### 2. Update API URL
In `src/services/api.js`, update the backend URL:
```javascript
const API_BASE_URL = 'http://localhost:8000';  // or your backend URL
```

### 3. Run the App
```bash
npx expo start
```

Then:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app on your phone

---

## Testing the App

### 1. Create Two Test Users
- Sign up as User A with handle "TestUser1"
- Sign up as User B with handle "TestUser2"

### 2. Test Proximity Matching
- Update location for both users (mock coordinates)
- Check "Nearby" screen to see each other
- Create a match

### 3. Test Chat
- Send messages between users
- Verify real-time message display

### 4. Test Identity Reveal
- Click "Reveal Identity" in chat
- Verify the other user sees the reveal status

### 5. Test Missions
- Complete daily missions
- Verify XP and level updates

---

## Project Structure

```
/app
├── /backend
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   ├── utils.py
│   └── /routers
│       ├── auth.py
│       ├── users.py
│       ├── matches.py
│       ├── chat.py
│       ├── reveal.py
│       └── missions.py
└── /mobile
    ├── App.js
    └── /src
        ├── /components
        ├── /screens
        └── /services
```
