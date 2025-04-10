import os
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash

# Create a database engine
DB_PATH = "stockrit.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

# Create a declarative base
Base = declarative_base()

# Define the association table for many-to-many relationship between users and stocks
favorites = Table(
    'favorites', 
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('stock_id', Integer, ForeignKey('stocks.id'))
)

class User(Base):
    """User model for storing user account information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    favorites = relationship('Stock', secondary=favorites, backref='users')
    
    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if password is correct."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

class Stock(Base):
    """Stock model for storing stock symbols and information"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Stock {self.symbol}>"

# Create a Session class
Session = scoped_session(sessionmaker(bind=engine))

def init_db():
    """Initialize the database and create all tables"""
    Base.metadata.create_all(engine)
    print("Database initialized with tables")
    
def add_user(username, email, password):
    """Add a new user to the database"""
    session = Session()
    
    # Check if username already exists
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        session.close()
        return False, "Username already exists. Please choose a different username."
    
    # Check if email already exists
    existing_email = session.query(User).filter_by(email=email).first()
    if existing_email:
        session.close()
        return False, "Email address already registered. Please use a different email."
    
    # Create new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    
    try:
        session.add(new_user)
        session.commit()
        session.close()
        return True, "User registered successfully!"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"An error occurred: {str(e)}"

def authenticate_user(username, password):
    """Authenticate a user"""
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    
    if user and user.check_password(password):
        session.close()
        return user
    
    session.close()
    return None

def add_favorite_stock(user_id, symbol, company_name=None):
    """Add a stock to a user's favorites"""
    session = Session()
    
    # Get user
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        session.close()
        return False, "User not found."
    
    # Check if stock exists in database
    stock = session.query(Stock).filter_by(symbol=symbol).first()
    
    # If stock doesn't exist, create it
    if not stock:
        stock = Stock(symbol=symbol, name=company_name)
        session.add(stock)
    
    # Check if user already has this stock in favorites
    for fav in user.favorites:
        if fav.symbol == symbol:
            session.close()
            return False, f"{symbol} is already in your favorites."
    
    # Add stock to user's favorites
    user.favorites.append(stock)
    
    try:
        session.commit()
        session.close()
        return True, f"{symbol} added to favorites."
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"An error occurred: {str(e)}"

def remove_favorite_stock(user_id, symbol):
    """Remove a stock from a user's favorites"""
    session = Session()
    
    # Get user
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        session.close()
        return False, "User not found."
    
    # Get stock
    stock = session.query(Stock).filter_by(symbol=symbol).first()
    if not stock:
        session.close()
        return False, f"Stock {symbol} not found."
    
    # Check if user has this stock in favorites
    found = False
    for fav in user.favorites:
        if fav.symbol == symbol:
            found = True
            break
    
    if not found:
        session.close()
        return False, f"{symbol} is not in your favorites."
    
    # Remove stock from user's favorites
    user.favorites.remove(stock)
    
    try:
        session.commit()
        session.close()
        return True, f"{symbol} removed from favorites."
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"An error occurred: {str(e)}"

def get_user_favorites(user_id):
    """Get a list of a user's favorite stocks"""
    session = Session()
    
    # Get user
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        session.close()
        return []
    
    # Get user's favorites
    favorites = user.favorites
    
    session.close()
    return favorites

# Initialize the database when imported
init_db()