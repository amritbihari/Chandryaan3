import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import format_large_number

def display_stock_info(stock_info):
    """
    Display stock information in a neatly formatted way.
    
    Parameters:
    stock_info (dict): Stock information dictionary
    """
    if not stock_info:
        st.error("Unable to fetch stock information. Please try again.")
        return
    
    # Add responsive styles for stock info
    st.markdown("""
    <style>
        /* Responsive styles for stock info on mobile */
        @media screen and (max-width: 768px) {
            .stMetric {
                padding: 8px 5px !important;
            }
            .stMetric label {
                font-size: 0.8rem !important;
            }
            .stMetric [data-testid="stMetricValue"] {
                font-size: 1.1rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with company name and current price with glassmorphism
    st.markdown(f"""
    <div class="glassmorphism" style="padding: 15px; margin-bottom: 15px; border-radius: 10px;">
        <h2 style="margin: 0; font-size: 1.6rem;" class="gradient-text">{stock_info['name']}</h2>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;">Sector: {stock_info['sector']} | Industry: {stock_info['industry']}</p>
        <div style="margin-top: 10px; font-size: 1.2rem; color: #4da6ff;">
            {stock_info['current_price'] if isinstance(stock_info['current_price'], str) else f"${stock_info['current_price']:.2f}"}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Market Cap",
            value=stock_info['market_cap']
        )
        st.metric(
            label="P/E Ratio",
            value=stock_info['pe_ratio']
        )
        st.metric(
            label="52 Week High",
            value=stock_info['52w_high'] if isinstance(stock_info['52w_high'], str) else f"${stock_info['52w_high']:.2f}"
        )
    
    with col2:
        st.metric(
            label="Volume",
            value=stock_info['volume']
        )
        st.metric(
            label="Forward P/E",
            value=stock_info['forward_pe']
        )
        st.metric(
            label="52 Week Low",
            value=stock_info['52w_low'] if isinstance(stock_info['52w_low'], str) else f"${stock_info['52w_low']:.2f}"
        )
    
    with col3:
        st.metric(
            label="Avg Volume",
            value=stock_info['avg_volume']
        )
        st.metric(
            label="Price to Book",
            value=stock_info['price_to_book']
        )
        st.metric(
            label="Beta",
            value=stock_info['beta']
        )
    
    # Analyst section
    st.subheader("Analyst Recommendations")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Target Price",
            value=stock_info['target_mean_price'] if isinstance(stock_info['target_mean_price'], str) else f"${stock_info['target_mean_price']:.2f}"
        )
    
    with col2:
        st.metric(
            label="Recommendation",
            value=stock_info['recommendation'].upper() if stock_info['recommendation'] != 'N/A' else 'N/A'
        )
    
    with col3:
        st.metric(
            label="ESG Score",
            value=stock_info['esg_score'] if stock_info['esg_score'] != 'N/A' else 'N/A'
        )
    
    # Dividend section if applicable
    if stock_info['dividend_rate'] != 'N/A' and stock_info['dividend_rate'] != 0:
        st.subheader("Dividend Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="Dividend Rate",
                value=stock_info['dividend_rate'] if isinstance(stock_info['dividend_rate'], str) else f"${stock_info['dividend_rate']:.2f}"
            )
        
        with col2:
            st.metric(
                label="Dividend Yield",
                value=stock_info['dividend_yield'] if isinstance(stock_info['dividend_yield'], str) else f"{stock_info['dividend_yield']:.2f}%"
            )

def display_popular_stocks(stocks_df):
    """
    Display popular stocks in a table.
    
    Parameters:
    stocks_df (pd.DataFrame): DataFrame containing popular stocks
    """
    if stocks_df is None or stocks_df.empty:
        st.error("Unable to fetch popular stocks data. Please try again.")
        return
    
    # Mobile-friendly title with glassmorphism
    st.markdown("""
    <div class="glassmorphism" style="padding: 12px; margin-bottom: 15px; border-radius: 10px;">
        <h3 style="margin: 0; font-size: 1.4rem;" class="gradient-text">Popular Stocks</h3>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.7;">
            Click on any stock symbol to analyze it
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add styles for responsive tables
    st.markdown("""
    <style>
        /* Responsive styles for dataframe on mobile */
        @media screen and (max-width: 768px) {
            .dataframe-container div[data-testid="stDataFrame"] {
                font-size: 0.8rem !important;
            }
            
            /* Hide less important columns on very small screens */
            @media screen and (max-width: 480px) {
                .dataframe-container [data-testid="stDataFrame"] th:nth-child(5),
                .dataframe-container [data-testid="stDataFrame"] td:nth-child(5),
                .dataframe-container [data-testid="stDataFrame"] th:nth-child(6),
                .dataframe-container [data-testid="stDataFrame"] td:nth-child(6) {
                    display: none !important;
                }
            }
        }
    </style>
    <div class="dataframe-container">
    """, unsafe_allow_html=True)
    
    # Make the table more interactive
    st.dataframe(
        stocks_df,
        column_config={
            "symbol": "Symbol",
            "name": "Company",
            "price": "Price",
            "change": "Change",
            "change_percent": "% Change",
            "market_cap": "Market Cap",
            "pe_ratio": "P/E Ratio"
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_loading_message():
    """Display a loading message with a spinner."""
    with st.spinner("Loading data, please wait..."):
        st.info("Fetching the latest stock data from Yahoo Finance.")

def show_error_message(message="Something went wrong. Please try again."):
    """Display an error message."""
    st.error(message)
