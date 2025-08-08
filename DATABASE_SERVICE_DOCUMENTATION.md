# Database Service Documentation

## Overview

This document provides a comprehensive explanation of the database service implementation in the Instagram Analytics application, covering the unified analytics engine, database caching strategy, and how all components work together to provide efficient data management and analytics.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Schema](#database-schema)
3. [UPSERT Strategy](#upsert-strategy)
4. [Analytics Service](#analytics-service)
5. [Data Flow](#data-flow)
6. [Caching Strategy](#caching-strategy)
7. [API Endpoints](#api-endpoints)
8. [Frontend Integration](#frontend-integration)
9. [Performance Optimizations](#performance-optimizations)

## Architecture Overview

The application follows a centralized architecture where all analytics calculations are handled by a unified analytics engine. This eliminates code redundancy and ensures consistent data processing across the application.

### Key Components:
- **Database Layer**: SQLite database with Profile and MediaPost tables
- **Instagram Service**: Handles API calls and data synchronization
- **Analytics Service**: Centralized analytics engine (850+ lines)
- **Frontend Dashboard**: Single unified dashboard consuming analytics data

```
Instagram API → Instagram Service → Database Storage → Analytics Service → Dashboard
```

## Database Schema

### Profile Table
```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    user_id TEXT,
    full_name TEXT,
    bio TEXT,
    followers_count INTEGER,
    following_count INTEGER,
    media_count INTEGER,
    profile_picture_url TEXT,
    is_business_account BOOLEAN,
    is_verified BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### MediaPost Table
```sql
CREATE TABLE media_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id TEXT UNIQUE NOT NULL,
    profile_id INTEGER,
    caption TEXT,
    media_type TEXT,
    media_url TEXT,
    thumbnail_url TEXT,
    permalink TEXT,
    timestamp TIMESTAMP,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles (id)
);
```

## UPSERT Strategy

The database implements an intelligent UPSERT (UPDATE or INSERT) strategy that preserves historical data while keeping engagement metrics current.

### How UPSERT Works:

1. **For Existing Posts**:
   - Updates engagement metrics (likes_count, comments_count)
   - Preserves original timestamp and creation data
   - Updates the `updated_at` field for tracking

2. **For New Posts**:
   - Inserts complete new record
   - Maintains historical timeline integrity

### Implementation Example:
```python
# From instagram_service.py
def update_media_posts(self, profile_id, media_data):
    for media in media_data:
        existing_post = db.session.query(MediaPost).filter_by(media_id=media['id']).first()
        
        if existing_post:
            # UPDATE: Preserve history, update engagement
            existing_post.likes_count = media.get('like_count', 0)
            existing_post.comments_count = media.get('comments_count', 0)
            existing_post.updated_at = datetime.utcnow()
        else:
            # INSERT: New post with complete data
            new_post = MediaPost(
                media_id=media['id'],
                profile_id=profile_id,
                caption=media.get('caption', ''),
                likes_count=media.get('like_count', 0),
                comments_count=media.get('comments_count', 0),
                timestamp=datetime.fromisoformat(media['timestamp'])
            )
            db.session.add(new_post)
    
    db.session.commit()
```

## Analytics Service

The centralized analytics service (`analytics_service.py`) serves as the single source of truth for all analytics calculations. It provides comprehensive metrics without redundant code across the application.

### Key Features:

#### 1. Comprehensive Dashboard Analytics
```python
def get_comprehensive_analytics(self, profile_id):
    """
    Returns complete analytics including:
    - Basic metrics (followers, posts, engagement)
    - Time period breakdown
    - Content type distribution
    - Hashtag trending analysis
    - Collaboration tracking
    - Favoured posting times
    """
```

#### 2. Time Period Analysis
```python
def _calculate_time_period_breakdown(self, posts):
    """
    Analyzes posting patterns across different time periods:
    - Morning (6 AM - 12 PM)
    - Afternoon (12 PM - 6 PM) 
    - Evening (6 PM - 12 AM)
    - Night (12 AM - 6 AM)
    """
```

#### 3. Daily Chart Data Generation
```python
def get_daily_chart_data(self, profile_id, days=30):
    """
    Generates time-series data for charts showing:
    - Daily post counts
    - Engagement trends
    - Growth patterns over specified period
    """
```

#### 4. Content Type Distribution
```python
def _get_content_type_distribution(self, posts):
    """
    Analyzes content types:
    - IMAGE: Single photos
    - VIDEO: Video content
    - CAROUSEL_ALBUM: Multi-photo posts
    """
```

#### 5. Hashtag Trending Analysis
```python
def _get_trending_hashtags(self, posts, limit=10):
    """
    Extracts and ranks hashtags by:
    - Frequency of use
    - Average engagement per hashtag
    - Trending patterns
    """
```

## Data Flow

### 1. Data Acquisition
```
Instagram API → fetch_instagram_data() → Raw API Response
```

### 2. Data Processing
```
Raw Data → Instagram Service → Database UPSERT → Stored Data
```

### 3. Analytics Generation
```
Database Query → Analytics Service → Calculated Metrics → API Response
```

### 4. Frontend Consumption
```
API Call → Dashboard Component → Data Visualization → User Interface
```

## Caching Strategy

### Database-Level Caching
The SQLite database serves as the primary cache, storing:
- **Historical Data**: Complete timeline of posts and engagement
- **Profile Information**: User details and account statistics
- **Engagement Metrics**: Updated likes and comments counts

### Benefits:
1. **Performance**: Eliminates repeated API calls
2. **Historical Analysis**: Enables trend analysis over time
3. **Offline Capability**: Data available without API dependency
4. **Rate Limit Management**: Reduces Instagram API usage

### Smart Update Logic:
```python
# Only updates engagement metrics, preserves historical context
if existing_post:
    existing_post.likes_count = new_likes_count  # Updated
    existing_post.comments_count = new_comments_count  # Updated
    existing_post.timestamp = original_timestamp  # Preserved
    existing_post.updated_at = datetime.utcnow()  # Tracking field
```

## API Endpoints

### Analytics Endpoints

#### 1. Comprehensive Analytics
```
GET /api/analytics/comprehensive/<profile_id>
```
Returns complete analytics dashboard data including all metrics and breakdowns.

#### 2. Daily Chart Data
```
GET /api/analytics/daily-chart/<profile_id>?days=<number>
```
Returns time-series data for chart visualizations over specified period.

#### 3. Basic Dashboard Data
```
GET /api/dashboard/<profile_id>
```
Returns essential dashboard metrics for quick overview.

### Data Management Endpoints

#### 1. Profile Data Fetch
```
POST /api/fetch-data/<profile_id>
```
Triggers Instagram API call and database synchronization.

#### 2. Profile Management
```
GET /api/profiles
POST /api/profiles
```
Handles profile creation and retrieval operations.

## Frontend Integration

### Centralized Data Fetching
The frontend Dashboard component uses the centralized analytics service:

```javascript
const fetchDashboardData = async () => {
    try {
        const [dashboardResponse, comprehensiveResponse, dailyChartResponse] = await Promise.all([
            fetch(`/api/dashboard/${profileId}`),
            fetch(`/api/analytics/comprehensive/${profileId}`),
            fetch(`/api/analytics/daily-chart/${profileId}?days=30`)
        ]);
        
        const dashboardData = await dashboardResponse.json();
        const comprehensiveData = await comprehensiveResponse.json();
        const dailyChartData = await dailyChartResponse.json();
        
        // Update state with centralized data
        setDashboardData(dashboardData);
        setComprehensiveAnalytics(comprehensiveData);
        setDailyChartData(dailyChartData);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
};
```

### Eliminated Redundancy
- **Before**: Multiple components calculating similar metrics
- **After**: Single analytics service providing all calculations
- **Result**: Consistent data across application, reduced code duplication

## Performance Optimizations

### 1. Database Indexing
```sql
CREATE INDEX idx_media_posts_profile_id ON media_posts(profile_id);
CREATE INDEX idx_media_posts_timestamp ON media_posts(timestamp);
CREATE INDEX idx_media_posts_media_id ON media_posts(media_id);
```

### 2. Efficient Queries
```python
# Single query for comprehensive analytics
posts = db.session.query(MediaPost)\
    .filter(MediaPost.profile_id == profile_id)\
    .order_by(MediaPost.timestamp.desc())\
    .all()
```

### 3. Calculated Fields
```python
# Pre-calculated engagement rates
engagement_rate = (total_engagement / total_followers) * 100 if total_followers > 0 else 0
average_likes = total_likes / len(posts) if posts else 0
```

### 4. Smart Data Updates
- Only updates changed engagement metrics
- Preserves historical data integrity
- Minimizes database write operations

## Best Practices Implemented

### 1. Single Responsibility Principle
- **Analytics Service**: Handles all metric calculations
- **Instagram Service**: Manages API interactions and data sync
- **Database Models**: Define data structure and relationships

### 2. DRY (Don't Repeat Yourself)
- Centralized analytics eliminates duplicate calculations
- Reusable service methods across different endpoints
- Consistent data processing logic

### 3. Data Integrity
- UPSERT strategy prevents data loss
- Timestamp preservation maintains historical accuracy
- Foreign key relationships ensure referential integrity

### 4. Scalability Considerations
- Modular service architecture
- Efficient database queries
- Cacheable API responses

## Troubleshooting Guide

### Common Issues and Solutions

1. **Data Not Updating**
   - Check Instagram API credentials
   - Verify profile_id mapping
   - Ensure UPSERT logic is functioning

2. **Performance Issues**
   - Review database indexes
   - Optimize query patterns
   - Check for N+1 query problems

3. **Analytics Discrepancies**
   - Verify analytics service calculations
   - Check data synchronization timestamps
   - Ensure consistent metric definitions

## Future Enhancements

### Potential Improvements

1. **Redis Caching Layer**
   - In-memory caching for frequently accessed data
   - Reduced database query load

2. **Background Job Processing**
   - Scheduled data synchronization
   - Asynchronous analytics calculation

3. **Data Archiving Strategy**
   - Long-term storage for historical data
   - Database size management

4. **Advanced Analytics**
   - Machine learning-based insights
   - Predictive engagement modeling

## Conclusion

The database service implementation provides a robust, efficient, and scalable foundation for Instagram analytics. The UPSERT strategy ensures data integrity while maintaining performance, and the centralized analytics service eliminates redundancy while providing comprehensive insights.

The architecture supports both real-time data updates and historical analysis, making it suitable for both immediate dashboard needs and long-term trend analysis. The modular design allows for easy maintenance and future enhancements while ensuring consistent data processing across the application.

---

*This documentation reflects the current state of the database service as of the unified analytics engine implementation and comprehensive dashboard enhancement.*
