# 🚀 Instagram Analytics Setup Guide

## Current Status

Your Instagram Analytics system is **running successfully** with the following components:

- ✅ **Backend (Flask API)**: Running on http://127.0.0.1:5000
- ✅ **Frontend (React)**: Running on http://localhost:3000
- ✅ **Database**: SQLite with sample data
- ⚠️ **Data Source**: Currently showing sample data (1 post per profile)

## 🔑 To Get Real Instagram Data

The system currently shows **sample data** because it needs a **Star API key** to fetch real Instagram data.

### Step 1: Get Star API Key

1. Go to [RapidAPI Star API](https://rapidapi.com/star-api/)
2. Subscribe to the Star API (they offer free tier)
3. Copy your API key from the RapidAPI dashboard

### Step 2: Configure API Key

**Option A: Create .env file (Recommended)**
```bash
# Create file: backend/.env
API_KEY=your_actual_rapidapi_key_here
```

**Option B: Set environment variable**
```bash
# Windows PowerShell
$env:API_KEY="your_actual_rapidapi_key_here"

# Then restart the backend
cd backend
python app.py
```

### Step 3: Restart Backend

After setting the API key, restart the backend server:
```bash
# Stop current server (Ctrl+C)
# Then restart
cd backend
python app.py
```

### Step 4: Fetch Real Data

1. Go to the **Dashboard** page
2. Click the **"Fetch Data"** button
3. Wait for data collection to complete
4. You should now see real Instagram data with hundreds/thousands of posts

## 📊 What You'll Get

With a valid API key, the system will collect:

- **Profile Information**: Followers, following, bio, verification status
- **Media Posts**: Photos, videos, reels with engagement metrics
- **Stories**: Recent stories and highlights
- **Analytics**: Engagement rates, best performing content, trends
- **Real-time Data**: Live data from Instagram via Star API

## 🔧 Troubleshooting

### "API_KEY not configured" Error
- Make sure you've set the API key correctly
- Check that the `.env` file is in the `backend/` folder
- Restart the backend server after setting the key

### "Failed to fetch user info" Error
- Verify your Star API subscription is active
- Check if the API key is valid
- Some profiles might be private or restricted

### Frontend Errors
- Clear browser cache and refresh
- Check browser console for JavaScript errors
- Ensure both frontend and backend are running

## 📁 File Structure

```
mentra project/
├── backend/
│   ├── .env                    # API key configuration
│   ├── app.py                  # Main Flask application
│   ├── services/               # Business logic
│   └── api/                    # API endpoints
├── frontend/
│   ├── src/
│   │   ├── pages/             # React components
│   │   └── services/          # API calls
│   └── package.json
└── README.md
```

## 🎯 Next Steps

1. **Get API Key**: Follow Step 1 above
2. **Configure**: Set up the API key
3. **Test**: Use the "Fetch Data" button
4. **Explore**: Check out all the analytics features

Once configured, you'll have a fully functional Instagram analytics system with real data!


