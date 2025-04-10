import streamlit as st
import re
from database import add_user, authenticate_user, add_favorite_stock, remove_favorite_stock, get_user_favorites

def init_session_state():
    """Initialize session state variables for authentication"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def login_form():
    """Display login form"""
    with st.form("login_form"):
        st.markdown('<p class="gradient-text" style="font-size: 1.5rem; text-align: center;">Log In</p>', unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please fill in all fields")
                return
            
            user = authenticate_user(username, password)
            if user:
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.logged_in = True
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def signup_form():
    """Display signup form"""
    with st.form("signup_form"):
        st.markdown('<p class="gradient-text" style="font-size: 1.5rem; text-align: center;">Create Account</p>', unsafe_allow_html=True)
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submit = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit:
            if not username or not email or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            is_valid, msg = validate_password(password)
            if not is_valid:
                st.error(msg)
                return
            
            success, message = add_user(username, email, password)
            if success:
                st.success(message)
                st.info("Please log in with your new account.")
            else:
                st.error(message)

def logout():
    """Log out the current user"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.logged_in = False
    st.success("You have been logged out.")
    st.rerun()

def auth_sidebar():
    """Display authentication sidebar"""
    init_session_state()
    
    with st.sidebar:
        if st.session_state.logged_in:
            st.markdown(f"""
            <div class="glassmorphism" style="padding: 15px; margin-bottom: 20px;">
                <p style="font-weight: 600; color: #4da6ff; margin-bottom: 10px;">User Profile</p>
                <p style="margin-bottom: 10px;">Logged in as: <strong>{st.session_state.username}</strong></p>
                <div style="display: flex; justify-content: flex-end;">
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Log Out", type="primary", use_container_width=True):
                logout()
        else:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                login_form()
                
            with tab2:
                signup_form()

def favorite_stocks_section(ticker):
    """Section to handle favorite stocks"""
    if not st.session_state.logged_in:
        return
    
    st.markdown("""
    <div class="glassmorphism" style="padding: 15px; margin-top: 20px; margin-bottom: 20px;">
        <h3 style="margin: 0; font-size: 1.2rem; color: #4da6ff;">Favorite Stocks</h3>
    </div>
    """, unsafe_allow_html=True)
    
    favorites = get_user_favorites(st.session_state.user_id)
    favorite_symbols = [stock.symbol for stock in favorites]
    
    if ticker in favorite_symbols:
        if st.button("Remove from Favorites", use_container_width=True):
            success, message = remove_favorite_stock(st.session_state.user_id, ticker)
            if success:
                st.success(message)
            else:
                st.error(message)
    else:
        if st.button("Add to Favorites", use_container_width=True):
            success, message = add_favorite_stock(
                st.session_state.user_id, 
                ticker,
                # If we have a company name, pass it along
                st.session_state.get('company_name', ticker)
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    
    if favorites:
        st.write("Your favorite stocks:")
        cols = st.columns(3)
        for i, stock in enumerate(favorites):
            with cols[i % 3]:
                if st.button(stock.symbol, key=f"fav_{stock.symbol}"):
                    st.session_state.selected_ticker = stock.symbol
                    st.rerun()
    else:
        st.info("You don't have any favorite stocks yet.")