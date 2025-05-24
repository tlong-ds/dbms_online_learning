import requests
import urllib3
import os
import sqlite3
import json
import shutil
import tempfile
from pathlib import Path
import platform
import time

# Suppress only the single InsecureRequestWarning from urllib3 needed.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_browser_cookie_from_chrome():
    """Get auth_token directly from the user's Chrome browser"""
    try:
        # Determine Chrome's cookie database location based on OS
        system = platform.system()
        cookie_path = None
        
        if system == "Darwin":  # macOS
            cookie_path = Path("~/Library/Application Support/Google/Chrome/Default/Cookies").expanduser()
        elif system == "Windows":
            cookie_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/User Data/Default/Cookies"
        elif system == "Linux":
            cookie_path = Path("~/.config/google-chrome/Default/Cookies").expanduser()
        
        if not cookie_path or not cookie_path.exists():
            print(f"Chrome cookie database not found at {cookie_path}")
            return None
            
        # Create a temporary copy of the database since Chrome may lock it
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, "chrome_cookies_temp")
        shutil.copy2(cookie_path, temp_path)
        
        # Connect to the copy
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        
        # Query for the auth_token cookie (note: database schema may vary)
        # This query is for newer Chrome versions
        try:
            cursor.execute(
                "SELECT name, value, host_key, path FROM cookies WHERE name = 'auth_token' AND host_key LIKE '%localhost%'"
            )
        except sqlite3.OperationalError:
            # Fallback for older Chrome versions
            cursor.execute(
                "SELECT name, value, host_key, path FROM cookies WHERE name = 'auth_token' AND host_key LIKE '%localhost%'"
            )
            
        cookies = cursor.fetchall()
        conn.close()
        
        # Clean up temp file
        shutil.rmtree(temp_dir)
        
        if not cookies:
            print("auth_token cookie not found in Chrome")
            return None
            
        print(f"Found {len(cookies)} auth_token cookies in Chrome")
        for cookie in cookies:
            name, value, domain, path = cookie
            print(f"  - Domain: {domain}, Path: {path}")
            
        # Return the first matching cookie's value
        return cookies[0][1]  # value is the second column
    
    except Exception as e:
        print(f"Error reading Chrome cookies: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_token_from_env_or_config():
    """Get token from environment variable or config file as fallback"""
    # Try environment variable first
    token = os.environ.get("AUTH_TOKEN")
    if token:
        print("Using auth_token from environment variable")
        return token
        
    # Try config file
    config_path = Path("~/.config/streamlit_auth.json").expanduser()
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                token = config.get("auth_token")
                if token:
                    print("Using auth_token from config file")
                    return token
        except Exception as e:
            print(f"Error reading config file: {e}")
    
    return None

# Create a session to maintain cookies
session = requests.Session()

# Try multiple methods to get an existing token
print("Attempting to get existing token from Chrome...")
existing_token = get_browser_cookie_from_chrome()

# If that fails, try from environment or config
if not existing_token:
    print("Attempting to get token from environment or config...")
    existing_token = get_token_from_env_or_config()
    
# If we have a token from any method
if existing_token:
    print(f"Found auth_token: {existing_token[:10]}...")
    # Set the cookie in our session
    session.cookies.set("auth_token", existing_token, domain="localhost", path="/")
    
    # Also try with IP address in case the server is accessed that way
    session.cookies.set("auth_token", existing_token, domain="0.0.0.0", path="/")

    # Verify the cookie was set by making a request to the FastAPI server
    try:
        get_cookie_response = session.get("http://localhost:8000/get_cookie", verify=False)
        print(f"Get cookie response: {get_cookie_response.json()}")
    except Exception as e:
        print(f"Error with localhost: {e}")
        try:
            get_cookie_response = session.get("http://0.0.0.0:8000/get_cookie", verify=False)
            print(f"Get cookie response: {get_cookie_response.json()}")
        except Exception as e:
            print(f"Error with 0.0.0.0: {e}")

    # Now use the session to make the request to whoami
    try:
        whoami_response = session.get("http://localhost:8000/whoami", verify=False)
        print(f"Using localhost for whoami")
    except Exception:
        try:
            whoami_response = session.get("http://0.0.0.0:8000/whoami", verify=False)
            print(f"Using 0.0.0.0 for whoami")
        except Exception as e:
            print(f"Error accessing whoami endpoint: {e}")
            exit(1)

    try:
        response = whoami_response.json()
        user_info = response.get("user_info")
        print(f"User info: {user_info}")
        if user_info is None:
            print("Not authenticated or no user information available")
    except requests.exceptions.JSONDecodeError:
        print("Response is not in JSON format:", whoami_response.text)
        print("Status code:", whoami_response.status_code)
else:
    print("No auth_token found. Please log in through the Streamlit app first.")
    
    # Helpful instructions for the user
    print("\nIf you've already logged in, you can try:")
    print("1. Make sure Chrome is closed before running this script")
    print("2. Open Chrome and visit http://localhost:8501 to log in")
    print("3. Run this script again")
    print("\nAlternatively, you can set the auth_token manually:")
    print("1. In Chrome, go to http://localhost:8501")
    print("2. Open Developer Tools (F12 or Cmd+Option+I on Mac)")
    print("3. Go to Application > Storage > Cookies > http://localhost:8501")
    print("4. Find the auth_token cookie and copy its value")
    print("5. Set an environment variable: export AUTH_TOKEN=your_token_value")
    print("6. Run this script again")