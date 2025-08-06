"""
Test script to verify Instagram Analytics setup
"""
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError:
        print("❌ Flask not installed")
        return False
    
    try:
        import flask_cors
        print("✅ Flask-CORS")
    except ImportError:
        print("❌ Flask-CORS not installed")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy")
    except ImportError:
        print("❌ Flask-SQLAlchemy not installed")
        return False
    
    try:
        import requests
        print("✅ Requests")
    except ImportError:
        print("❌ Requests not installed")
        return False
    
    try:
        import pandas
        print("✅ Pandas")
    except ImportError:
        print("❌ Pandas not installed")
        return False
    
    try:
        import pytz
        print("✅ Pytz")
    except ImportError:
        print("❌ Pytz not installed")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv")
    except ImportError:
        print("❌ Python-dotenv not installed")
        return False
    
    return True

def test_database():
    """Test database connection and table creation"""
    try:
        from models.database import db
        from app import create_app
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test basic query
            from models.database import Profile
            profiles = Profile.query.all()
            print(f"✅ Database query successful ({len(profiles)} profiles found)")
            
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_api_endpoints():
    """Test if Flask app starts correctly"""
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Flask app responds correctly")
                return True
            else:
                print(f"❌ Flask app returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    print("Instagram Analytics - Setup Verification")
    print("=" * 50)
    
    print("\n1. Testing package imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing database setup...")
    database_ok = test_database()
    
    print("\n3. Testing Flask application...")
    api_ok = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if imports_ok and database_ok and api_ok:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run 'python app.py' to start the backend server")
        print("2. In another terminal, run 'npm start' in the frontend folder")
        print("3. Open http://localhost:3000 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        if not imports_ok:
            print("- Install missing packages: pip install -r requirements-dev.txt")
        if not database_ok:
            print("- Check your .env file configuration")
        if not api_ok:
            print("- Check Flask app configuration")
    
    return 0 if (imports_ok and database_ok and api_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
