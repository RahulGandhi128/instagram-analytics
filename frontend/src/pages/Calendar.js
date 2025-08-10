import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Star, MapPin, Clock } from 'lucide-react';

const Calendar = ({ showNotification }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [holidays, setHolidays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(null);
  const [calendarView, setCalendarView] = useState('month'); // 'month' or 'year'

  // Fetch Indian holidays from free API
  useEffect(() => {
    fetchHolidays(currentDate.getFullYear());
  }, [currentDate]);

  const fetchHolidays = async (year) => {
    setLoading(true);
    try {
      // Using calendarific.com free API (requires API key but has generous free tier)
      // Alternative: We'll use a combination of static data and date-fns for Indian holidays
      
      // For demo, I'll use static data for major Indian holidays
      // In production, you can integrate with APIs like:
      // 1. Calendarific API: https://calendarific.com/
      // 2. Abstract API: https://app.abstractapi.com/api/holidays/
      // 3. Public Holidays API: https://date.nager.at/api/v3/publicholidays/{year}/IN
      
      const response = await fetch(`https://date.nager.at/api/v3/publicholidays/${year}/IN`);
      
      if (response.ok) {
        const data = await response.json();
        const formattedHolidays = data.map(holiday => ({
          date: holiday.date,
          name: holiday.name,
          localName: holiday.localName,
          type: holiday.types?.includes('Public') ? 'public' : 'observance',
          description: `${holiday.name} - National holiday in India`,
          category: 'national'
        }));
        
        // Add additional cultural and regional holidays
        const additionalHolidays = getAdditionalIndianHolidays(year);
        setHolidays([...formattedHolidays, ...additionalHolidays]);
      } else {
        // Fallback to static holidays if API fails
        const staticHolidays = getStaticIndianHolidays(year);
        setHolidays(staticHolidays);
      }
    } catch (error) {
      console.error('Error fetching holidays:', error);
      // Fallback to static holidays
      const staticHolidays = getStaticIndianHolidays(year);
      setHolidays(staticHolidays);
    } finally {
      setLoading(false);
    }
  };

  // Static holidays for fallback
  const getStaticIndianHolidays = (year) => {
    return [
      { date: `${year}-01-01`, name: 'New Year\'s Day', type: 'public', category: 'national', description: 'Start of the Gregorian calendar year' },
      { date: `${year}-01-26`, name: 'Republic Day', type: 'public', category: 'national', description: 'Commemorates the Constitution of India' },
      { date: `${year}-08-15`, name: 'Independence Day', type: 'public', category: 'national', description: 'Independence from British rule' },
      { date: `${year}-10-02`, name: 'Gandhi Jayanti', type: 'public', category: 'national', description: 'Birthday of Mahatma Gandhi' },
      { date: `${year}-03-08`, name: 'Holi', type: 'public', category: 'religious', description: 'Festival of Colors' },
      { date: `${year}-04-14`, name: 'Ram Navami', type: 'public', category: 'religious', description: 'Birthday of Lord Rama' },
      { date: `${year}-08-11`, name: 'Krishna Janmashtami', type: 'public', category: 'religious', description: 'Birthday of Lord Krishna' },
      { date: `${year}-09-07`, name: 'Ganesh Chaturthi', type: 'public', category: 'religious', description: 'Birthday of Lord Ganesha' },
      { date: `${year}-10-24`, name: 'Dussehra', type: 'public', category: 'religious', description: 'Victory of good over evil' },
      { date: `${year}-11-12`, name: 'Diwali', type: 'public', category: 'religious', description: 'Festival of Lights' },
      { date: `${year}-12-25`, name: 'Christmas Day', type: 'public', category: 'religious', description: 'Birth of Jesus Christ' },
      // Content planning occasions
      { date: `${year}-02-14`, name: 'Valentine\'s Day', type: 'observance', category: 'social', description: 'Day of love and romance' },
      { date: `${year}-03-08`, name: 'Women\'s Day', type: 'observance', category: 'social', description: 'International Women\'s Day' },
      { date: `${year}-05-12`, name: 'Mother\'s Day', type: 'observance', category: 'social', description: 'Honoring mothers and motherhood' },
      { date: `${year}-06-16`, name: 'Father\'s Day', type: 'observance', category: 'social', description: 'Honoring fathers and fatherhood' },
      { date: `${year}-06-21`, name: 'Yoga Day', type: 'observance', category: 'health', description: 'International Day of Yoga' },
      { date: `${year}-10-31`, name: 'Halloween', type: 'observance', category: 'social', description: 'Spooky celebrations' }
    ];
  };

  // Additional cultural holidays
  const getAdditionalIndianHolidays = (year) => {
    return [
      { date: `${year}-04-13`, name: 'Baisakhi', type: 'regional', category: 'regional', description: 'Harvest festival in Punjab' },
      { date: `${year}-08-19`, name: 'Raksha Bandhan', type: 'observance', category: 'family', description: 'Bond between brothers and sisters' },
      { date: `${year}-09-05`, name: 'Teachers\' Day', type: 'observance', category: 'education', description: 'Honoring teachers and educators' },
      { date: `${year}-11-14`, name: 'Children\'s Day', type: 'observance', category: 'family', description: 'Celebrating children' },
      { date: `${year}-01-15`, name: 'Makar Sankranti', type: 'regional', category: 'regional', description: 'Harvest festival' },
      { date: `${year}-09-10`, name: 'Karva Chauth', type: 'observance', category: 'family', description: 'Fasting for spouse\'s well-being' }
    ];
  };

  // Calendar navigation
  const navigateMonth = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(currentDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const navigateYear = (direction) => {
    const newDate = new Date(currentDate);
    newDate.setFullYear(currentDate.getFullYear() + direction);
    setCurrentDate(newDate);
  };

  // Get holidays for a specific date
  const getHolidaysForDate = (date) => {
    // Create local date string in YYYY-MM-DD format to avoid timezone issues
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;
    
    return holidays.filter(holiday => holiday.date === dateStr);
  };

  // Get calendar days for current month
  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const current = new Date(startDate);
    
    for (let i = 0; i < 42; i++) {
      const dayHolidays = getHolidaysForDate(current);
      days.push({
        date: new Date(current),
        isCurrentMonth: current.getMonth() === month,
        isToday: current.toDateString() === new Date().toDateString(),
        holidays: dayHolidays
      });
      current.setDate(current.getDate() + 1);
    }
    
    return days;
  };

  // Get category color
  const getCategoryColor = (category) => {
    const colors = {
      national: 'bg-red-100 text-red-800 border-red-200',
      religious: 'bg-orange-100 text-orange-800 border-orange-200',
      regional: 'bg-blue-100 text-blue-800 border-blue-200',
      social: 'bg-pink-100 text-pink-800 border-pink-200',
      family: 'bg-green-100 text-green-800 border-green-200',
      health: 'bg-purple-100 text-purple-800 border-purple-200',
      education: 'bg-yellow-100 text-yellow-800 border-yellow-200'
    };
    return colors[category] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const calendarDays = getCalendarDays();
  
  // Fix upcoming holidays calculation to avoid timezone issues
  const today = new Date();
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  
  const upcomingHolidays = holidays
    .filter(holiday => holiday.date >= todayStr)
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(0, 8);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <CalendarIcon className="h-8 w-8 text-orange-500 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Indian Calendar</h1>
                <p className="text-gray-600">Holidays, festivals, and occasions for content planning</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCalendarView(calendarView === 'month' ? 'year' : 'month')}
                className="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
              >
                {calendarView === 'month' ? 'Year View' : 'Month View'}
              </button>
              <div className="text-right">
                <p className="text-sm text-gray-500">Today</p>
                <p className="font-semibold text-gray-900">
                  {new Date().toLocaleDateString('en-IN', { 
                    weekday: 'long',
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>
          </div>

          {/* Data Source Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center">
              <MapPin className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <h3 className="font-medium text-blue-800">Indian Calendar Data</h3>
                <p className="text-blue-700 text-sm mt-1">
                  Includes national holidays, major festivals, and content planning occasions. 
                  Data sourced from Nager.Date API with additional cultural events.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Calendar */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              {/* Calendar Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => calendarView === 'month' ? navigateMonth(-1) : navigateYear(-1)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="h-5 w-5 text-gray-600" />
                  </button>
                  <h2 className="text-xl font-semibold text-gray-900">
                    {calendarView === 'month' 
                      ? `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`
                      : currentDate.getFullYear()
                    }
                  </h2>
                  <button
                    onClick={() => calendarView === 'month' ? navigateMonth(1) : navigateYear(1)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ChevronRight className="h-5 w-5 text-gray-600" />
                  </button>
                </div>
                <button
                  onClick={() => setCurrentDate(new Date())}
                  className="px-4 py-2 text-sm bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors"
                >
                  Today
                </button>
              </div>

              {calendarView === 'month' ? (
                <>
                  {/* Days of Week Header */}
                  <div className="grid grid-cols-7 gap-1 mb-2">
                    {dayNames.map(day => (
                      <div key={day} className="p-2 text-center text-sm font-medium text-gray-500">
                        {day}
                      </div>
                    ))}
                  </div>

                  {/* Calendar Grid */}
                  <div className="grid grid-cols-7 gap-1">
                    {calendarDays.map((day, index) => (
                      <div
                        key={index}
                        onClick={() => setSelectedDate(day.date)}
                        className={`
                          min-h-[100px] p-2 border border-gray-200 cursor-pointer hover:bg-gray-50 transition-colors
                          ${!day.isCurrentMonth ? 'bg-gray-50 text-gray-400' : ''}
                          ${day.isToday ? 'bg-orange-50 border-orange-300' : ''}
                          ${selectedDate?.toDateString() === day.date.toDateString() ? 'bg-blue-50 border-blue-300' : ''}
                        `}
                      >
                        <div className="flex justify-between items-start mb-1">
                          <span className={`text-sm font-medium ${day.isToday ? 'text-orange-600' : ''}`}>
                            {day.date.getDate()}
                          </span>
                          {day.holidays.length > 0 && (
                            <Star className="h-3 w-3 text-orange-500" />
                          )}
                        </div>
                        
                        {/* Holiday indicators */}
                        <div className="space-y-1">
                          {day.holidays.slice(0, 2).map((holiday, idx) => (
                            <div
                              key={idx}
                              className={`text-xs p-1 rounded border ${getCategoryColor(holiday.category)}`}
                              title={holiday.description}
                            >
                              {holiday.name.length > 12 ? `${holiday.name.substring(0, 12)}...` : holiday.name}
                            </div>
                          ))}
                          {day.holidays.length > 2 && (
                            <div className="text-xs text-gray-500">
                              +{day.holidays.length - 2} more
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                /* Year View - Show months */
                <div className="grid grid-cols-3 gap-4">
                  {monthNames.map((month, index) => {
                    const monthHolidays = holidays.filter(holiday => {
                      const holidayMonth = new Date(holiday.date).getMonth();
                      return holidayMonth === index;
                    });
                    
                    return (
                      <div
                        key={month}
                        onClick={() => {
                          const newDate = new Date(currentDate);
                          newDate.setMonth(index);
                          setCurrentDate(newDate);
                          setCalendarView('month');
                        }}
                        className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                      >
                        <h3 className="font-semibold text-gray-900 mb-2">{month}</h3>
                        <div className="text-sm text-gray-600">
                          {monthHolidays.length} holiday{monthHolidays.length !== 1 ? 's' : ''}
                        </div>
                        <div className="mt-2 space-y-1">
                          {monthHolidays.slice(0, 3).map((holiday, idx) => (
                            <div key={idx} className="text-xs text-gray-500 truncate">
                              {holiday.name}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Selected Date Details */}
            {selectedDate && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  {selectedDate.toLocaleDateString('en-IN', { 
                    weekday: 'long',
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </h3>
                
                {getHolidaysForDate(selectedDate).length > 0 ? (
                  <div className="space-y-3">
                    {getHolidaysForDate(selectedDate).map((holiday, index) => (
                      <div key={index} className={`p-3 rounded-lg border ${getCategoryColor(holiday.category)}`}>
                        <h4 className="font-medium">{holiday.name}</h4>
                        <p className="text-sm mt-1">{holiday.description}</p>
                        <div className="flex items-center mt-2 text-xs">
                          <span className="capitalize">{holiday.type}</span>
                          <span className="mx-2">•</span>
                          <span className="capitalize">{holiday.category}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No special occasions on this date.</p>
                )}
              </div>
            )}

            {/* Upcoming Holidays */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Clock className="h-5 w-5 mr-2 text-orange-500" />
                Upcoming Holidays
              </h3>
              
              {loading ? (
                <div className="space-y-3">
                  {[1, 2, 3, 4].map(i => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 bg-gray-200 rounded mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {upcomingHolidays.map((holiday, index) => {
                    // Parse date properly to avoid timezone issues
                    const [year, month, day] = holiday.date.split('-').map(Number);
                    const holidayDate = new Date(year, month - 1, day); // month is 0-based in JS Date
                    
                    const today = new Date();
                    const todayLocal = new Date(today.getFullYear(), today.getMonth(), today.getDate());
                    const holidayLocal = new Date(holidayDate.getFullYear(), holidayDate.getMonth(), holidayDate.getDate());
                    
                    const daysUntil = Math.ceil((holidayLocal - todayLocal) / (1000 * 60 * 60 * 24));
                    
                    return (
                      <div key={index} className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{holiday.name}</h4>
                          <p className="text-sm text-gray-600">
                            {holidayDate.toLocaleDateString('en-IN', { 
                              month: 'short', 
                              day: 'numeric' 
                            })}
                          </p>
                          <span className={`inline-block mt-1 px-2 py-1 text-xs rounded-full ${getCategoryColor(holiday.category)}`}>
                            {holiday.category}
                          </span>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-900">
                            {daysUntil === 0 ? 'Today' : 
                             daysUntil === 1 ? 'Tomorrow' : 
                             `${daysUntil} days`}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Holiday Categories Legend */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Categories</h3>
              <div className="space-y-2">
                {[
                  { key: 'national', label: 'National Holidays' },
                  { key: 'religious', label: 'Religious Festivals' },
                  { key: 'regional', label: 'Regional Celebrations' },
                  { key: 'social', label: 'Social Occasions' },
                  { key: 'family', label: 'Family Events' },
                  { key: 'health', label: 'Health & Wellness' },
                  { key: 'education', label: 'Educational' }
                ].map(category => (
                  <div key={category.key} className="flex items-center">
                    <div className={`w-4 h-4 rounded border mr-3 ${getCategoryColor(category.key)}`}></div>
                    <span className="text-sm text-gray-700">{category.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calendar;
