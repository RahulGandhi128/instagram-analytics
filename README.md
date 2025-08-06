# Instagram Analytics Dashboard

A comprehensive Instagram analytics application built with Flask (backend) and React (frontend) that provides detailed insights into Instagram account performance, engagement rates, and content analysis.

## 🚀 Features

### **Profile Management**
- ✅ Add/Delete Instagram accounts dynamically
- ✅ Real-time engagement rate calculations using Instagram formula: `(Average Engagement per Post / Followers) × 100`
- ✅ Profile picture display with fallback handling
- ✅ Verification status and privacy indicators

### **Analytics Dashboard**
- ✅ Summary statistics with key metrics
- ✅ Interactive charts and visualizations
- ✅ Time period controls (7, 14, 30, 90 days)
- ✅ Period-over-period comparisons (week/month/custom)
- ✅ Data export functionality (CSV)

### **Performance Insights**
- ✅ Top and bottom performing posts analysis
- ✅ Media type performance (posts, reels, carousels)
- ✅ Optimal posting times analysis
- ✅ Daily and hourly engagement patterns
- ✅ Comprehensive recommendations with IST timezone

### **Data Management**
- ✅ Instagram Star API integration for real-time data
- ✅ SQLite database with comprehensive data models
- ✅ Automatic data fetching and updates
- ✅ Historical data preservation
- ✅ Flexible period analysis

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Database
- **Instagram Star API** - Data source
- **Python** - Core language

### Frontend
- **React** - UI framework
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **JavaScript/ES6** - Core language
- Real-time dashboard with live data updates
- Responsive design with Tailwind CSS
- Beautiful Instagram-inspired color scheme

### 🗄️ Database Support
- **PostgreSQL**: Production-ready with connection pooling
- **SQLite**: Local development fallback
- **Automated migrations**: Database schema management
- **Background tasks**: Scheduled data fetching

## Project Structure

```
mentra project/
├── backend/                 # Flask API Server
│   ├── api/
│   │   └── routes.py       # API endpoints
│   ├── models/
│   │   └── database.py     # SQLAlchemy models
│   ├── services/
│   │   └── instagram_service.py # Instagram API integration
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # React Application
│   ├── public/
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   └── App.js         # Main application
│   ├── package.json       # Node dependencies
│   └── tailwind.config.js # Tailwind CSS config
└── app.py                 # Legacy standalone app
```

## Setup Instructions

### 1. Backend Setup (Flask)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your settings:
# - DATABASE_URL (for PostgreSQL)
# - API_KEY (Instagram Star API key)
# - USE_SQLITE=True (for local development)

# Run the Flask application
python app.py
```

The backend will be available at `http://localhost:5000`

### 2. Frontend Setup (React)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. PostgreSQL Setup (Production)

```bash
# Install PostgreSQL
# Create database
createdb instagram_analytics

# Update .env file
DATABASE_URL=postgresql://username:password@localhost:5432/instagram_analytics
USE_SQLITE=False
```

## API Endpoints

### Profile Management
- `GET /api/profiles` - Get all profiles
- `GET /api/profiles/{username}` - Get specific profile

### Media & Content
- `GET /api/media` - Get media posts (with filtering)
- `GET /api/stories` - Get current stories

### Analytics
- `GET /api/analytics/insights` - Performance insights
- `GET /api/analytics/weekly-comparison` - Week-over-week data
- `GET /api/analytics/daily-metrics` - Daily metrics for charts

### Data Management
- `POST /api/fetch-data` - Trigger data fetching
- `GET /api/export/csv` - Export data to CSV
- `GET /api/stats/summary` - Summary statistics

## Configuration

### Environment Variables (.env)

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/instagram_analytics
USE_SQLITE=True  # Set to False for PostgreSQL

# API Configuration
API_KEY=your_star_api_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
PORT=5000
```

### Instagram API Configuration

The application uses the Star API for Instagram data:
- **Profile Data**: `get_web_profile_info`
- **Media Posts**: `get_media`  
- **Stories**: `get_stories`

Tracked accounts: `["naukridotcom", "swiggyindia", "zomato", "instagram"]`

## Key Features Implementation

### 1. Data Fetching Service
```python
# Backend service handles:
- Profile data synchronization
- Media post collection
- Stories tracking
- Daily metrics calculation
- Rate limiting and error handling
```

### 2. Analytics Engine
```python
# Advanced analytics include:
- Engagement rate calculations  
- Optimal posting time analysis
- Media type performance comparison
- Week-over-week trend analysis
- Top/bottom performer identification
```

### 3. Export Functionality
```javascript
// CSV export with customizable data:
- Media posts with engagement metrics
- Profile data with follower counts
- Stories data with expiration times
- Daily metrics for trend analysis
```

### 4. Visualization Dashboard
```javascript
// Interactive charts for:
- Daily engagement trends (Line charts)
- Media type performance (Pie charts)  
- Posting time optimization (Bar charts)
- Performance radar (Radar charts)
```

## Deployment

### Production Deployment

1. **Backend (Flask)**:
   ```bash
   # Use Gunicorn for production
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Frontend (React)**:
   ```bash
   # Build for production
   npm run build
   # Serve with nginx or similar
   ```

3. **Database**: Configure PostgreSQL with connection pooling

4. **Environment**: Set production environment variables

### Docker Deployment (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Development

### Adding New Features

1. **Backend**: Add routes in `api/routes.py`
2. **Frontend**: Create components in `src/pages/` or `src/components/`
3. **Database**: Update models in `models/database.py`
4. **API Integration**: Extend `services/instagram_service.py`

### Testing

```bash
# Backend testing
cd backend
python -m pytest

# Frontend testing  
cd frontend
npm test
```

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running and credentials are correct
2. **API Rate Limits**: The service includes rate limiting (2s delays between requests)
3. **CORS Issues**: Backend is configured for `localhost:3000` frontend
4. **Missing Dependencies**: Run `pip install -r requirements.txt` and `npm install`

### Debug Mode

Set `FLASK_ENV=development` in `.env` for detailed error messages.

## Future Enhancements

- [ ] Real-time notifications for new posts
- [ ] Advanced competitor analysis
- [ ] Custom date range filtering
- [ ] Email reports scheduling
- [ ] Multi-account dashboard views
- [ ] Machine learning for engagement prediction
- [ ] Integration with other social platforms

## License

This project is for educational and business use. Ensure compliance with Instagram's Terms of Service when using their data.
