# Gia-Su-AI Backend - Quickstart Guide

**Updated: 2025-01-17**

## Prerequisites

- Python 3.11+
- MongoDB (local hoặc Atlas)
- Google AI API key
- Git

---

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd Gia-Su-AI-BE
```

---

## Step 2: Setup Virtual Environment

```powershell
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4: Configure Environment Variables

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file
notepad .env  # Windows
# nano .env   # Linux/Mac
```

**Required environment variables:**
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=belearning_db
GOOGLE_API_KEY=your-google-ai-api-key-here
JWT_SECRET_KEY=your-random-secret-key-for-development
```

**Get Google AI API Key:**
1. Visit: https://aistudio.google.com/app/apikey
2. Click "Create new API key"
3. Copy the key to your `.env` file

---

## Step 5: Initialize Database (Optional)

```bash
python scripts/init_data.py
python scripts/create_indexes.py
```

---

## Step 6: Start Server

```powershell
uvicorn app.main:app --reload
```

Server will be running at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs ⭐ (Interactive API documentation)
- **ReDoc**: http://localhost:8000/redoc (Read-only API documentation)
- **Health Check**: http://localhost:8000/health

---

## Testing API with Swagger UI

1. Open http://localhost:8000/docs
2. Click the **"Authorize"** button (top-right)
3. Register a new user:
   - Find `/auth/register` endpoint
   - Enter username, email, password
   - Click "Execute"
4. Login to get JWT token:
   - Find `/auth/login` endpoint
   - Enter credentials
   - Copy the token from response
5. Paste token in "Authorize" dialog
6. Now you can test protected endpoints!

---

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running locally or check your Atlas connection string in `.env`

**API Key Error:**
- Verify `GOOGLE_API_KEY` is correctly set in `.env`
- Restart the server after updating `.env`

**Module Import Error:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

---

## Project Structure

- `app/` - Main application entry point
- `controllers/` - API endpoint handlers
- `routers/` - API route definitions
- `services/` - Business logic
- `schemas/` - Pydantic data models
- `models/` - Database models
- `middleware/` - Authentication & RBAC
- `config/` - Configuration files
- `scripts/` - Utility scripts

---

## Next Steps

- Read [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for testing procedures
- Check controller files for available endpoints
- Review services for business logic implementation

---

