import streamlit as st
import streamlit.components.v1 as components
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
FASTAPI_URL = os.getenv("AUTH_URL", "http://0.0.0.0:8000")

def get_token_from_browser():
    """
    Extract auth_token from browser cookies and return it.
    This is a one-shot function that gets the token and returns it.
    """
    # Use a unique key for each call to ensure component is refreshed
    key = f"token_extractor_{int(time.time())}"
    
    # Create a placeholder to display messages
    placeholder = st.empty()
    
    # Extract token using JavaScript
    html_code = """
    <script>
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }
    
    // Get the auth_token cookie
    const token = getCookie('auth_token');
    console.log('Auth token from cookie:', token);
    
    // Update URL parameter
    if (token) {
        const url = new URL(window.location.href);
        url.searchParams.set('token', token);
        history.replaceState({}, '', url);
    }
    </script>
    """
    
    # Inject JavaScript to extract cookie
    components.html(html_code, height=0)
    
    # Get token from URL parameters
    token = st.query_params.get("token", None)
    
    if token:
        placeholder.success("Token successfully retrieved from browser")
        return token
    else:
        placeholder.warning("No token found in browser cookies")
        return None

def validate_token(token):
    """
    Validate the token by calling the whoami API endpoint.
    Returns user_info dictionary if valid, None otherwise.
    """
    if not token:
        return None
        
    try:
        response = requests.get(
            f"{FASTAPI_URL}/whoami", 
            cookies={"auth_token": token}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("user_info")
        else:
            st.warning(f"API returned status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error validating token: {str(e)}")
        return None

def get_and_validate_token():
    """
    Combined function to get token from browser and validate it.
    Returns (token, user_info) tuple if successful, (None, None) otherwise.
    """
    token = get_token_from_browser()
    user_info = validate_token(token) if token else None
    return token, user_info

def set_user_token(username, role):
    """
    Sets a new token for the given username and role.
    Returns the token if successful, None otherwise.
    """
    try:
        response = requests.get(
            f"{FASTAPI_URL}/set_cookie?username={username}&role={role}"
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        return None
    except Exception:
        return None

def clear_token():
    """
    Clear the auth_token cookie.
    """
    try:
        requests.get(f"{FASTAPI_URL}/logout")
        # Also clear session state
        for key in ["token", "username", "role", "login"]:
            if key in st.session_state:
                del st.session_state[key]
        return True
    except Exception:
        return False
