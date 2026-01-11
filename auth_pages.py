"""
Authentication Pages for Speech Therapy Platform

Beautiful login and signup pages with role-based access control.
"""

import streamlit as st
import hashlib
from utils.supabase_client import get_supabase_client


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def login_page():
    """Display login page with modern UI."""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3.5rem; font-weight: 800; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       margin-bottom: 0.5rem;'>
                🗣️ AI Speech Therapy
            </h1>
            <p style='font-size: 1.2rem; color: #666; margin-top: 0;'>
                Welcome back! Please login to continue your practice.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Login Form
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("### 🔐 Login")
                
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    key="login_username"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    submit = st.form_submit_button(
                        "🚀 Login",
                        use_container_width=True,
                        type="primary"
                    )
                
                with col_btn2:
                    signup_redirect = st.form_submit_button(
                        "📝 Sign Up",
                        use_container_width=True
                    )
                
                if signup_redirect:
                    st.session_state.auth_page = "signup"
                    st.rerun()
                
                if submit:
                    if not username or not password:
                        st.error("❌ Please fill in all fields")
                    else:
                        # Authenticate user
                        user = authenticate_user(username, password)
                        
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user['user_id']
                            st.session_state.username = user['username']
                            st.session_state.user_role = user['role']
                            st.session_state.full_name = user.get('full_name', username)
                            st.success(f"✅ Welcome back, {user['username']}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
    
    st.markdown('</div>', unsafe_allow_html=True)


def signup_page():
    """Display signup page with role selection."""
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3.5rem; font-weight: 800; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       margin-bottom: 0.5rem;'>
                🗣️ AI Speech Therapy
            </h1>
            <p style='font-size: 1.2rem; color: #666; margin-top: 0;'>
                Create your account and start improving your pronunciation!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Signup Form
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("### ✨ Create Account")
                
                full_name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name",
                    key="signup_fullname"
                )
                
                username = st.text_input(
                    "Username",
                    placeholder="Choose a unique username",
                    key="signup_username",
                    help="Username must be unique"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Create a strong password",
                    key="signup_password",
                    help="Minimum 6 characters"
                )
                
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password",
                    key="signup_confirm_password"
                )
                
                role = st.selectbox(
                    "Account Type",
                    options=["user", "admin"],
                    format_func=lambda x: "👤 Regular User" if x == "user" else "👨‍💼 Administrator",
                    help="Select your account type"
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    submit = st.form_submit_button(
                        "🎉 Create Account",
                        use_container_width=True,
                        type="primary"
                    )
                
                with col_btn2:
                    login_redirect = st.form_submit_button(
                        "🔙 Back to Login",
                        use_container_width=True
                    )
                
                if login_redirect:
                    st.session_state.auth_page = "login"
                    st.rerun()
                
                if submit:
                    # Validation
                    if not all([full_name, username, password, confirm_password]):
                        st.error("❌ Please fill in all fields")
                    elif len(password) < 6:
                        st.error("❌ Password must be at least 6 characters long")
                    elif password != confirm_password:
                        st.error("❌ Passwords do not match")
                    else:
                        # Create user
                        success, message = create_user(username, password, full_name, role)
                        
                        if success:
                            st.success(f"✅ {message}")
                            st.info("🔐 You can now login with your credentials")
                            st.balloons()
                            # Redirect to login after 2 seconds
                            import time
                            time.sleep(2)
                            st.session_state.auth_page = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def authenticate_user(username: str, password: str):
    """
    Authenticate user with username and password.
    
    Args:
        username: User's username
        password: User's password (will be hashed)
    
    Returns:
        dict: User data if authenticated, None otherwise
    """
    try:
        supabase = get_supabase_client()
        password_hash = hash_password(password)
        
        # Query user by username and password
        response = supabase.from_('user_profiles').select('*').eq('username', username).eq('password_hash', password_hash).execute()
        
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            # Ensure user_id field exists (using the UUID from user_id column)
            if 'user_id' not in user_data:
                user_data['user_id'] = user_data.get('id')
            return user_data
        else:
            return None
            
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None


def create_user(username: str, password: str, full_name: str, role: str = 'user'):
    """
    Create a new user account.
    
    Args:
        username: Unique username
        password: User password (will be hashed)
        full_name: User's full name
        role: User role ('user' or 'admin')
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        supabase = get_supabase_client()
        
        # Check if username already exists
        existing = supabase.from_('user_profiles').select('username').eq('username', username).execute()
        
        if existing.data and len(existing.data) > 0:
            return False, "Username already exists. Please choose another one."
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user profile
        user_data = {
            'username': username,
            'password_hash': password_hash,
            'full_name': full_name,
            'role': role
        }
        
        response = supabase.from_('user_profiles').insert(user_data).execute()
        
        if response.data:
            return True, "Account created successfully!"
        else:
            return False, "Failed to create account. Please try again."
            
    except Exception as e:
        return False, f"Error creating account: {str(e)}"


def logout():
    """Logout current user."""
    # Clear authentication state
    for key in ['authenticated', 'user_id', 'username', 'user_role', 'full_name']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reset to login page
    st.session_state.auth_page = "login"
    st.rerun()


def check_authentication():
    """
    Check if user is authenticated.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    return st.session_state.get('authenticated', False)


def require_authentication():
    """
    Decorator/function to require authentication.
    Shows login page if not authenticated.
    
    Returns:
        bool: True if authenticated, False otherwise
    """
    if not check_authentication():
        # Initialize auth page
        if 'auth_page' not in st.session_state:
            st.session_state.auth_page = "login"
        
        # Show appropriate page
        if st.session_state.auth_page == "signup":
            signup_page()
        else:
            login_page()
        
        return False
    
    return True


def require_admin():
    """
    Check if current user is an admin.
    
    Returns:
        bool: True if admin, False otherwise
    """
    return st.session_state.get('user_role') == 'admin'
