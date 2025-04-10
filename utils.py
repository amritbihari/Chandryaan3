import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_stock_data(ticker, period="1y"):
    """
    Fetch stock data from Yahoo Finance.
    
    Parameters:
    ticker (str): Stock ticker symbol
    period (str): Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
    pd.DataFrame: Historical stock data
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        return None

def get_stock_info(ticker):
    """
    Fetch stock information from Yahoo Finance.
    
    Parameters:
    ticker (str): Stock ticker symbol
    
    Returns:
    dict: Stock information
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        return None

def calculate_technical_indicators(data):
    """
    Calculate technical indicators from stock data.
    
    Parameters:
    data (pd.DataFrame): Historical stock data
    
    Returns:
    pd.DataFrame: Stock data with technical indicators
    """
    if data is None or data.empty:
        return None
    
    # Make a copy to avoid modifying the original
    df = data.copy()
    
    # Moving averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    
    # Bollinger Bands
    df['20MA'] = df['Close'].rolling(window=20).mean()
    df['20STD'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['20MA'] + (df['20STD'] * 2)
    df['Lower_Band'] = df['20MA'] - (df['20STD'] * 2)
    
    # RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD (Moving Average Convergence Divergence)
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
    
    # Volume EMA
    df['Volume_EMA'] = df['Volume'].ewm(span=20, adjust=False).mean()
    
    return df

def create_price_chart(data, ticker):
    """
    Create an interactive price chart using Plotly.
    
    Parameters:
    data (pd.DataFrame): Historical stock data with technical indicators
    ticker (str): Stock ticker symbol
    
    Returns:
    go.Figure: Plotly figure object
    """
    if data is None or data.empty:
        return None
    
    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.02, 
                        row_heights=[0.7, 0.3],
                        subplot_titles=(f"{ticker} Stock Price", "Volume"))
    
    # Add price candles
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Price",
            increasing_line_color='#26a69a', 
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # Add moving averages
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MA20'],
            name="MA20",
            line=dict(color='#ffeb3b', width=1)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MA50'],
            name="MA50",
            line=dict(color='#ff9800', width=1)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MA200'],
            name="MA200",
            line=dict(color='#f44336', width=1)
        ),
        row=1, col=1
    )
    
    # Add Bollinger Bands
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Upper_Band'],
            name="Upper Bollinger Band",
            line=dict(color='rgba(173, 216, 230, 0.5)', width=1),
            showlegend=True
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Lower_Band'],
            name="Lower Bollinger Band",
            line=dict(color='rgba(173, 216, 230, 0.5)', width=1),
            fill='tonexty',
            fillcolor='rgba(173, 216, 230, 0.1)',
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Add volume
    colors = ['#26a69a' if row['Close'] >= row['Open'] else '#ef5350' for index, row in data.iterrows()]
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name="Volume",
            marker_color=colors
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Volume_EMA'],
            name="Volume EMA",
            line=dict(color='#ffeb3b', width=1.5)
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f"{ticker} Stock Analysis",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=60, b=10)
    )
    
    # Style the candles
    fig.update_xaxes(
        rangeslider_visible=False,
        gridcolor='rgba(255, 255, 255, 0.1)',
        gridwidth=1
    )
    
    fig.update_yaxes(
        gridcolor='rgba(255, 255, 255, 0.1)',
        gridwidth=1
    )
    
    return fig

def create_technical_indicators_chart(data, ticker):
    """
    Create charts for technical indicators using Plotly.
    
    Parameters:
    data (pd.DataFrame): Historical stock data with technical indicators
    ticker (str): Stock ticker symbol
    
    Returns:
    go.Figure: Plotly figure object
    """
    if data is None or data.empty:
        return None
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, 
                        row_heights=[0.5, 0.5],
                        subplot_titles=("RSI (Relative Strength Index)", "MACD (Moving Average Convergence Divergence)"))
    
    # Add RSI
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['RSI'],
            name="RSI",
            line=dict(color='#26a69a', width=1.5)
        ),
        row=1, col=1
    )
    
    # Add RSI reference lines
    fig.add_trace(
        go.Scatter(
            x=[data.index[0], data.index[-1]],
            y=[70, 70],
            name="Overbought (70)",
            line=dict(color='#ef5350', width=1, dash='dash'),
            showlegend=True
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=[data.index[0], data.index[-1]],
            y=[30, 30],
            name="Oversold (30)",
            line=dict(color='#26a69a', width=1, dash='dash'),
            showlegend=True
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=[data.index[0], data.index[-1]],
            y=[50, 50],
            name="Neutral (50)",
            line=dict(color='#9e9e9e', width=1, dash='dash'),
            showlegend=True
        ),
        row=1, col=1
    )
    
    # Add MACD
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['MACD'],
            name="MACD",
            line=dict(color='#2196f3', width=1.5)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['Signal_Line'],
            name="Signal Line",
            line=dict(color='#ff9800', width=1.5)
        ),
        row=2, col=1
    )
    
    # Add MACD Histogram
    colors = ['#26a69a' if val >= 0 else '#ef5350' for val in data['MACD_Histogram']]
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['MACD_Histogram'],
            name="MACD Histogram",
            marker_color=colors
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=f"{ticker} Technical Indicators",
        height=600,
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=10, t=60, b=10)
    )
    
    fig.update_xaxes(
        gridcolor='rgba(255, 255, 255, 0.1)',
        gridwidth=1
    )
    
    fig.update_yaxes(
        gridcolor='rgba(255, 255, 255, 0.1)',
        gridwidth=1
    )
    
    # Set y-axis range for RSI
    fig.update_yaxes(range=[0, 100], row=1, col=1)
    
    return fig

def get_financial_summary(ticker):
    """
    Create a financial summary for the given stock.
    
    Parameters:
    ticker (str): Stock ticker symbol
    
    Returns:
    dict: Financial summary data
    """
    info = get_stock_info(ticker)
    if not info:
        return None
    
    # Calculate additional metrics
    pe_ratio = info.get('trailingPE', None)
    forward_pe = info.get('forwardPE', None)
    peg_ratio = info.get('pegRatio', None)
    price_to_book = info.get('priceToBook', None)
    enterprise_value = info.get('enterpriseValue', None)
    enterprise_to_revenue = info.get('enterpriseToRevenue', None)
    enterprise_to_ebitda = info.get('enterpriseToEbitda', None)
    
    summary = {
        'name': info.get('shortName', 'N/A'),
        'sector': info.get('sector', 'N/A'),
        'industry': info.get('industry', 'N/A'),
        'market_cap': info.get('marketCap', 'N/A'),
        'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
        'open': info.get('open', 'N/A'),
        'high': info.get('dayHigh', 'N/A'),
        'low': info.get('dayLow', 'N/A'),
        'previous_close': info.get('previousClose', 'N/A'),
        'volume': info.get('volume', 'N/A'),
        'avg_volume': info.get('averageVolume', 'N/A'),
        '52w_high': info.get('fiftyTwoWeekHigh', 'N/A'),
        '52w_low': info.get('fiftyTwoWeekLow', 'N/A'),
        'pe_ratio': pe_ratio,
        'forward_pe': forward_pe,
        'peg_ratio': peg_ratio,
        'price_to_book': price_to_book,
        'enterprise_value': enterprise_value,
        'enterprise_to_revenue': enterprise_to_revenue,
        'enterprise_to_ebitda': enterprise_to_ebitda,
        'beta': info.get('beta', 'N/A'),
        'dividend_rate': info.get('dividendRate', 'N/A'),
        'dividend_yield': info.get('dividendYield', 'N/A') * 100 if info.get('dividendYield') else 'N/A',
        'target_mean_price': info.get('targetMeanPrice', 'N/A'),
        'recommendation': info.get('recommendationKey', 'N/A'),
        'esg_score': info.get('esgScore', 'N/A')
    }
    
    # Format numbers for better readability
    for key, value in summary.items():
        if isinstance(value, (int, float)) and key not in ['dividend_yield', 'pe_ratio', 'forward_pe', 'peg_ratio', 'price_to_book', 'beta', 'enterprise_to_revenue', 'enterprise_to_ebitda']:
            if value > 1_000_000_000:
                summary[key] = f"${value/1_000_000_000:.2f}B"
            elif value > 1_000_000:
                summary[key] = f"${value/1_000_000:.2f}M"
            elif value > 1_000:
                summary[key] = f"${value/1_000:.2f}K"
            else:
                summary[key] = f"${value:.2f}"
        elif isinstance(value, float) and key in ['dividend_yield', 'pe_ratio', 'forward_pe', 'peg_ratio', 'price_to_book', 'beta', 'enterprise_to_revenue', 'enterprise_to_ebitda']:
            summary[key] = f"{value:.2f}"
    
    return summary

def get_popular_stocks():
    """
    Returns a list of popular stocks and their basic info.
    
    Returns:
    pd.DataFrame: DataFrame containing popular stocks and their info
    """
    popular_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'V', 'WMT']
    stock_data = []
    
    for ticker in popular_tickers:
        info = get_stock_info(ticker)
        if info:
            stock_data.append({
                'symbol': ticker,
                'name': info.get('shortName', 'N/A'),
                'price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
                'change': info.get('regularMarketChange', 'N/A'),
                'change_percent': info.get('regularMarketChangePercent', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A')
            })
    
    # Create DataFrame
    df = pd.DataFrame(stock_data)
    
    # Format numbers
    if not df.empty:
        # Format price
        if 'price' in df.columns and df['price'].dtype != object:
            df['price'] = df['price'].apply(lambda x: f"${x:.2f}" if isinstance(x, (int, float)) else x)
        
        # Format change
        if 'change' in df.columns and df['change'].dtype != object:
            df['change'] = df['change'].apply(lambda x: f"{x:+.2f}" if isinstance(x, (int, float)) else x)
        
        # Format change percent
        if 'change_percent' in df.columns and df['change_percent'].dtype != object:
            df['change_percent'] = df['change_percent'].apply(lambda x: f"{x:+.2f}%" if isinstance(x, (int, float)) else x)
        
        # Format market cap
        if 'market_cap' in df.columns and df['market_cap'].dtype != object:
            df['market_cap'] = df['market_cap'].apply(lambda x: f"${x/1_000_000_000:.2f}B" if isinstance(x, (int, float)) and x > 1_000_000_000 else 
                                                    (f"${x/1_000_000:.2f}M" if isinstance(x, (int, float)) and x > 1_000_000 else x))
        
        # Format PE ratio
        if 'pe_ratio' in df.columns and df['pe_ratio'].dtype != object:
            df['pe_ratio'] = df['pe_ratio'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
    
    return df

def format_large_number(num):
    """
    Format large numbers for better readability.
    
    Parameters:
    num (int/float): Number to format
    
    Returns:
    str: Formatted number
    """
    if not isinstance(num, (int, float)):
        return "N/A"
    
    if num > 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num > 1_000_000:
        return f"${num/1_000_000:.2f}M"
    elif num > 1_000:
        return f"${num/1_000:.2f}K"
    else:
        return f"${num:.2f}"
