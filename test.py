import streamlit as st
import streamlit.components.v1 as components
import json
import requests

st.title("JS Cookie Extraction Test")

# Add a rerun button for easier testing
if st.button("Rerun Test"):
    st.rerun()

# First, attempt to directly extract the auth_token cookie with JavaScript
components.html("""
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
        
        if (token) {
            fetch("http://0.0.0.0:8000/whoami", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
            }).then(res => res.json()).then(data => {
            document.body.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            });

        // Store it in a div for Streamlit to access
        const tokenEl = window.parent.document.getElementById("token-display");
        if (tokenEl) {
            tokenEl.innerText = token || "No token found in cookies";
        }
        
        // Also attempt the whoami request to see server response
        fetch("http://0.0.0.0:8000/whoami", {
            method: "GET",
            credentials: "include",
            headers: {
                "Accept": "application/json"
            }
        })
        .then(res => {
            console.log('Response status:', res.status);
            if (!res.ok) {
                throw new Error(`HTTP error! Status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            console.log('API response:', data);
            
            // Send token back to Streamlit via URL parameters
            if (token) {
                // Create a new URL with the current location and add the token as a parameter
                const url = new URL(window.parent.location.href);
                url.searchParams.set('auth_token', token);
                
                // Only redirect if we don't already have the token in the URL
                // This prevents an infinite reload loop    
                if (!window.parent.location.href.includes('auth_token=')) {
                    console.log('Redirecting with token in URL');
                    
                    // Send token more reliably through a Streamlit component event
                    if (window.parent.Streamlit) {
                        console.log('Using Streamlit component communication');
                        window.parent.Streamlit.setComponentValue(token);
                    } else {
                        // Fallback to URL parameter approach
                        window.parent.location.href = url.toString();
                    }
                }
            } else {
                console.log('No token found to send back to Streamlit');
            }
        })
        .catch(err => {
            console.error('Fetch error:', err);
            document.getElementById('debug-info').innerText = 'Error: ' + err.message;
        });
    </script>
    <div id="debug-info"></div>
""", height=0)

# Try to get token from the component
token_from_component = st.session_state.get("cookie_component")
if token_from_component:
    st.success(f"Token successfully retrieved from component: {token_from_component[:10]}...")
    token_from_url = token_from_component  # Use this token for API calls
else:
    # Display the extracted information
    st.markdown("### Cookie Token Value:")
    token_container = st.empty()
    token_container.markdown('<div id="token-display">Waiting for token...</div>', unsafe_allow_html=True)

    # Check for the token in URL parameters (added by JavaScript)
    token_from_url = st.query_params.get("auth_token")
    
    # Debug information about query parameters
    st.write("Debug - URL Parameters:", dict(st.query_params))
    st.write("Debug - token_from_url type:", type(token_from_url))
    st.write("Debug - token_from_url value:", token_from_url)

if token_from_url:
    st.success(f"Token successfully retrieved from URL parameters: {token_from_url[:10]}...")
    
    # Make API call with the token
    try:
        response = requests.get(
            "http://0.0.0.0:8000/whoami",
            cookies={"auth_token": token_from_url}
        )
        st.write("API Response using token from browser:")
        st.json(response.json())
    except Exception as e:
        st.error(f"Error calling API with token: {str(e)}")


# Server-side API call for comparison
st.markdown("---")
st.markdown("### Server-side API Check:")
try:
    # Get the token from an input field as fallback
    token_input = st.text_input("Enter token manually if needed:")
    if st.button("Check Token on Server Side"):
        if token_input:
            response = requests.get("http://0.0.0.0:8000/whoami", 
                                  cookies={"auth_token": token_input})
            st.json(response.json())
        else:
            st.warning("Please enter a token")
except Exception as e:
    st.error(f"Server-side API error: {str(e)}")

# Additional debugging information
st.markdown("---")
st.markdown("### Debugging Info:")
st.markdown("1. Make sure the FastAPI server is running at http://0.0.0.0:8000")
st.markdown("2. Check that you're logged in (the auth_token cookie should be set)")
st.markdown("3. Verify CORS settings in cookie_api.py allow this Streamlit app's origin")
st.markdown("4. Open browser console (F12) to see more detailed error messages")

# Login helper
st.markdown("---")
st.markdown("### Login Helper:")
username = st.text_input("Username for login:")
role = st.selectbox("Role", ["Learner", "Instructor"])
if st.button("Set Cookie"):
    try:
        response = requests.get(f"http://0.0.0.0:8000/set_cookie?username={username}&role={role}")
        st.success(f"Cookie set response: {response.json()}")
        st.markdown("Now refresh the page to see if the token is detected")
    except Exception as e:
        st.error(f"Error setting cookie: {str(e)}")