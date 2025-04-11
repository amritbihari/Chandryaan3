import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import custom modules
from utils import (
    get_stock_data, 
    get_stock_info, 
    calculate_technical_indicators, 
    create_price_chart, 
    create_technical_indicators_chart,
    get_financial_summary,
    get_popular_stocks
)
from components import (
    display_stock_info,
    display_popular_stocks,
    show_loading_message,
    show_error_message
)
# Import authentication module
from auth import auth_sidebar, init_session_state, favorite_stocks_section

# Set page config
st.set_page_config(
    page_title="StockRit",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #4da6ff;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #fafafa;
        opacity: 0.8;
        margin-top: 0;
    }
    .highlight {
        color: #4da6ff;
        font-weight: 600;
    }
    .card {
        border-radius: 5px;
        background-color: #1a1f2c;
        padding: 20px;
        margin-bottom: 20px;
    }
    .divider {
        margin-top: 1rem;
        margin-bottom: 1rem;
        border: 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Add custom CSS for the modern transparent look
st.markdown("""
<style>
    .glassmorphism {
        background: rgba(26, 31, 44, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .feature-box {
        background: rgba(26, 31, 44, 0.4);
        backdrop-filter: blur(5px);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    .feature-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        background: rgba(26, 31, 44, 0.6);
    }
    .gradient-text {
        background: linear-gradient(90deg, #4da6ff, #a64dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Add responsive styles for header
st.markdown("""
<style>
    .hero-container {
        text-align: center;
        padding: 40px 20px;
        margin-bottom: 30px;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 15px;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: #e0e0e0;
        margin-bottom: 25px;
    }
    
    .hero-description {
        max-width: 700px;
        margin: 0 auto;
        font-size: 1.1rem;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.8);
    }
    
    /* Responsive styles for tablets */
    @media screen and (max-width: 992px) {
        .hero-title {
            font-size: 3rem;
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
        }
        
        .hero-description {
            font-size: 1rem;
        }
    }
    
    /* Responsive styles for mobile devices */
    @media screen and (max-width: 768px) {
        .hero-container {
            padding: 25px 15px;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
            margin-bottom: 15px;
        }
        
        .hero-description {
            font-size: 0.9rem;
        }
    }
</style>

<div class="hero-container glassmorphism">
    <h1 class="hero-title gradient-text">StockRit</h1>
    <div class="hero-subtitle">Intelligent Stock Analysis Platform</div>
    <div class="hero-description">
        Unlock the power of data-driven investment decisions with real-time market analysis, 
        interactive charts, and comprehensive financial metrics.
    </div>
</div>
""", unsafe_allow_html=True)

# Feature section with hover effects - Responsive grid for all devices
st.markdown("""
<style>
    /* Responsive grid for feature boxes */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 25px;
        margin-bottom: 40px;
    }
    
    /* Media query for tablets */
    @media screen and (max-width: 992px) {
        .feature-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        .feature-box {
            padding: 15px !important;
        }
        .feature-box h3 {
            font-size: 1.1rem !important;
        }
        .feature-box p {
            font-size: 0.85rem !important;
        }
    }
    
    /* Media query for mobile devices */
    @media screen and (max-width: 768px) {
        .feature-grid {
            grid-template-columns: 1fr;
            gap: 15px;
        }
        .feature-box {
            padding: 15px !important;
        }
    }
</style>

<div class="feature-grid">
    <div class="feature-box" style="padding: 20px; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 10px; color: #4da6ff;">📊</div>
        <h3 style="font-size: 1.2rem; margin-bottom: 8px; color: #4da6ff;">Real-time Data</h3>
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Live stock prices and metrics</p>
    </div>
    <div class="feature-box" style="padding: 20px; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 10px; color: #4da6ff;">📈</div>
        <h3 style="font-size: 1.2rem; margin-bottom: 8px; color: #4da6ff;">Analytics</h3>
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">RSI, MACD & technical indicators</p>
    </div>
    <div class="feature-box" style="padding: 20px; text-align: center;">
        <div style="font-size: 2rem; margin-bottom: 10px; color: #4da6ff;">🔍</div>
        <h3 style="font-size: 1.2rem; margin-bottom: 8px; color: #4da6ff;">Insights</h3>
        <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Track top performing stocks</p>
    </div>
</div>

# Add responsive styles for the call-to-action box
<div class="glassmorphism" style="padding: 20px; margin-bottom: 30px; text-align: center;">
    <h2 style="margin-top: 0; font-size: 1.6rem; margin-bottom: 12px;" class="gradient-text">Ready to Analyze?</h2>
    <p style="margin-bottom: 15px; color: rgba(255, 255, 255, 0.8); font-size: 0.95rem;">
        Enter any stock symbol in the sidebar to see comprehensive analysis, interactive charts, and key financial metrics.
    </p>
    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin-top: 15px;">
        <span style="background: rgba(77, 166, 255, 0.2); padding: 6px 12px; border-radius: 20px; color: #4da6ff; font-weight: 600; font-size: 0.9rem; margin-bottom: 5px;">AAPL</span>
        <span style="background: rgba(77, 166, 255, 0.2); padding: 6px 12px; border-radius: 20px; color: #4da6ff; font-weight: 600; font-size: 0.9rem; margin-bottom: 5px;">MSFT</span>
        <span style="background: rgba(77, 166, 255, 0.2); padding: 6px 12px; border-radius: 20px; color: #4da6ff; font-weight: 600; font-size: 0.9rem; margin-bottom: 5px;">TSLA</span>
        <span style="background: rgba(77, 166, 255, 0.2); padding: 6px 12px; border-radius: 20px; color: #4da6ff; font-weight: 600; font-size: 0.9rem; margin-bottom: 5px;">AMZN</span>
        <span style="background: rgba(77, 166, 255, 0.2); padding: 6px 12px; border-radius: 20px; color: #4da6ff; font-weight: 600; font-size: 0.9rem; margin-bottom: 5px;">GOOGL</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for stock analysis
if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = "AAPL"

if 'selected_period' not in st.session_state:
    st.session_state.selected_period = "1y"
    
# Initialize authentication session state
init_session_state()

# Sidebar
with st.sidebar:
    st.markdown('<p class="gradient-text" style="font-size: 2rem; font-weight: 700; text-align: center; margin-bottom: 15px;">StockRit</p>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Authentication section
    auth_sidebar()
    
    # Stock search - with glassmorphism style
    st.markdown('<div class="glassmorphism" style="padding: 15px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<p style="font-weight: 600; color: #4da6ff; margin-bottom: 10px;">Stock Search</p>', unsafe_allow_html=True)
    
    ticker_input = st.text_input(
        "Enter Stock Symbol",
        value=st.session_state.selected_ticker,
        help="Type any valid stock ticker symbol (e.g., AAPL, MSFT, TSLA)"
    )
    
    # Period selection
    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo", 
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y"
    }
    
    selected_period_name = st.selectbox(
        "Select Time Period",
        options=list(period_options.keys()),
        index=list(period_options.keys()).index("1 Year"),
        help="Choose the historical time period for analysis"
    )
    
    selected_period = period_options[selected_period_name]
    
    # Button to update ticker and period with styling
    if st.button("Analyze Stock", 
                help="Click to analyze the selected stock",
                use_container_width=True):
        if ticker_input:
            ticker_input = ticker_input.upper().strip()
            st.session_state.selected_ticker = ticker_input
            st.session_state.selected_period = selected_period
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
    
    # About section with glassmorphism style
    st.markdown('<div class="glassmorphism" style="padding: 15px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown('<p style="font-weight: 600; color: #4da6ff; margin-bottom: 10px;">About</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.8);">
        StockRit provides professional-grade stock analysis using real-time data from Yahoo Finance.
        <br><br>
        Track price movements, analyze technical indicators, and discover market trends to make better-informed investment decisions.
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add version and copyright
    st.markdown('<p style="font-size: 0.7rem; opacity: 0.7; text-align: center; margin-top: 20px;">© 2025 StockRit v1.0</p>', unsafe_allow_html=True)

# Get ticker and period from session state
ticker = st.session_state.selected_ticker
period = st.session_state.selected_period

# Define empty data_with_indicators to avoid errors
data_with_indicators = None

# Add responsive style for the content header
st.markdown("""
<style>
    .content-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    
    .content-title {
        margin: 0;
        font-size: 1.8rem;
    }
    
    .period-badge {
        background: rgba(77, 166, 255, 0.2);
        padding: 5px 15px;
        border-radius: 20px;
        color: #4da6ff;
        font-weight: 600;
        margin-left: 15px;
    }
    
    /* Mobile responsive adjustments */
    @media screen and (max-width: 768px) {
        .content-header {
            flex-direction: column;
            align-items: flex-start;
            padding: 12px;
        }
        
        .content-title {
            font-size: 1.5rem;
            margin-bottom: 10px;
        }
        
        .period-badge {
            margin-left: 0;
            align-self: flex-start;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main content - with responsive glassmorphism style for section heading
st.markdown(f"""
<div class="glassmorphism content-header">
    <h2 class="content-title gradient-text">Analysis for {ticker}</h2>
    <div class="period-badge">{period}</div>
</div>
""", unsafe_allow_html=True)

# Use tabs to organize content with styled headers
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Technical Analysis", "🔍 Popular Stocks"])

with tab1:
    # Show loading message
    show_loading_message()
    
    # Get stock data and info
    stock_data = get_stock_data(ticker, period)
    stock_info = get_financial_summary(ticker)
    
    if stock_data is None or stock_data.empty:
        show_error_message(f"Unable to fetch data for {ticker}. Please check the symbol and try again.")
    else:
        # Save company name for favorite stocks
        if stock_info and isinstance(stock_info, dict) and 'name' in stock_info:
            st.session_state.company_name = stock_info['name']
        
        # Display favorite button for logged in users
        if st.session_state.logged_in:
            favorite_stocks_section(ticker)
        
        # Display financial summary
        display_stock_info(stock_info)
        
        # Calculate indicators and create chart
        data_with_indicators = calculate_technical_indicators(stock_data)
        price_chart = create_price_chart(data_with_indicators, ticker)
        
        # Display price chart
        st.plotly_chart(price_chart, use_container_width=True)

with tab2:
    if 'data_with_indicators' not in locals() or data_with_indicators is None:
        show_loading_message()
        stock_data = get_stock_data(ticker, period)
        if stock_data is None or stock_data.empty:
            show_error_message(f"Unable to fetch data for {ticker}. Please check the symbol and try again.")
        else:
            data_with_indicators = calculate_technical_indicators(stock_data)
    
    if 'data_with_indicators' in locals() and data_with_indicators is not None:
        # Technical indicators chart
        tech_chart = create_technical_indicators_chart(data_with_indicators, ticker)
        st.plotly_chart(tech_chart, use_container_width=True)
        
        # Display the latest indicator values
        latest_data = data_with_indicators.iloc[-1]
        
        st.subheader("Latest Technical Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi_value = latest_data['RSI']
            if rsi_value > 70:
                rsi_status = "Overbought"
            elif rsi_value < 30:
                rsi_status = "Oversold"
            else:
                rsi_status = "Neutral"
            
            st.metric(
                label="RSI (14)",
                value=f"{rsi_value:.2f}",
                delta=rsi_status
            )
        
        with col2:
            macd_value = latest_data['MACD']
            signal_value = latest_data['Signal_Line']
            macd_status = "Bullish" if macd_value > signal_value else "Bearish"
            
            st.metric(
                label="MACD",
                value=f"{macd_value:.2f}",
                delta=macd_status
            )
        
        with col3:
            upper_band = latest_data['Upper_Band']
            lower_band = latest_data['Lower_Band']
            close_price = latest_data['Close']
            
            if close_price > upper_band:
                bb_status = "Above Upper Band"
            elif close_price < lower_band:
                bb_status = "Below Lower Band"
            else:
                bb_status = "Within Bands"
            
            st.metric(
                label="Bollinger Bands",
                value=f"${close_price:.2f}",
                delta=bb_status
            )
        
        with col4:
            ma20 = latest_data['MA20']
            ma50 = latest_data['MA50']
            ma200 = latest_data['MA200']
            
            if ma20 > ma50 and ma50 > ma200:
                ma_status = "Strong Uptrend"
            elif ma20 < ma50 and ma50 < ma200:
                ma_status = "Strong Downtrend"
            elif ma20 > ma50 and ma50 < ma200:
                ma_status = "Potential Bullish Crossover"
            else:
                ma_status = "Mixed Signals"
            
            st.metric(
                label="Moving Averages",
                value=f"${ma20:.2f} (MA20)",
                delta=ma_status
            )

with tab3:
    show_loading_message()
    
    # Get popular stocks data
    popular_stocks = get_popular_stocks()
    
    if popular_stocks is None or popular_stocks.empty:
        show_error_message("Unable to fetch popular stocks data. Please try again.")
    else:
        # Display popular stocks
        display_popular_stocks(popular_stocks)
        
        # Add a message about clicking on a stock
        st.info("Click on a stock symbol in the table to analyze it!")
        
        # Add a more detailed explanation
        st.markdown("""
        ### How to Use This Dashboard
        
        1. **Search for a stock** by entering its ticker symbol in the sidebar
        2. **Change the time period** to view different historical ranges
        3. **Explore the tabs** to see different analyses:
           - **Overview**: See the stock price chart and financial summary
           - **Technical Analysis**: View technical indicators like RSI, MACD, and Bollinger Bands
           - **Popular Stocks**: View a list of popular stocks and their current metrics
        
        ### Understanding the Charts
        
        - **Candlestick Chart**: Shows the open, high, low, and close prices for each period
        - **Moving Averages**: Help identify trends (MA20, MA50, MA200)
        - **Bollinger Bands**: Show volatility and potential reversal points
        - **Volume**: Indicates the trading activity
        - **RSI**: Measures momentum (values above 70 are considered overbought, below 30 oversold)
        - **MACD**: Shows trend direction and momentum changes
        """)

# Footer with glassmorphism style
st.markdown('<div class="glassmorphism" style="padding: 20px; margin-top: 30px;">', unsafe_allow_html=True)
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
    <div style="font-size: 0.9rem; opacity: 0.8; color: rgba(255, 255, 255, 0.9);">
        Data provided by Yahoo Finance
    </div>
    <div class="gradient-text" style="font-size: 1.2rem; font-weight: 700;">
        StockRit
    </div>
</div>

<div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 20px;">
    This platform is designed for informational purposes only and should not be considered financial advice.
</div>

<div style="text-align: center; padding-top: 15px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
    <p style="font-size: 0.9rem; margin-bottom: 5px;">
        Created by <a href="https://amritbihari.netlify.app" target="_blank" style="color: #4da6ff; text-decoration: none; font-weight: 600;">Amrit Bihari</a>
    </p>
    <p style="font-size: 0.8rem; opacity: 0.6;">© 2025 StockRit • Version 1.0</p>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
