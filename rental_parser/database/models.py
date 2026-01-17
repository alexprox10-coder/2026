"""
Database models for rental property parser
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class RentalListing(Base):
    """Model for storing rental property listings"""
    __tablename__ = 'rental_listings'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False, index=True)  # cian, yandex, avito
    listing_id = Column(String(100), nullable=False, unique=True, index=True)  # Unique ID from platform
    url = Column(Text, nullable=False)
    phone = Column(String(50))

    # Property details
    title = Column(Text)
    address = Column(Text)
    price = Column(Float)
    rooms = Column(Integer)
    area = Column(Float)
    floor = Column(Integer)
    total_floors = Column(Integer)

    # Additional info
    description = Column(Text)
    raw_data = Column(Text)  # JSON string with all scraped data

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    sent_to_manager = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    manager_id = Column(String(100), nullable=True)

    # Anti-duplicate
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RentalListing {self.platform}:{self.listing_id} - {self.price}₽>"


class ParsingSession(Base):
    """Track parsing sessions for monitoring"""
    __tablename__ = 'parsing_sessions'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    listings_found = Column(Integer, default=0)
    listings_new = Column(Integer, default=0)
    status = Column(String(20), default='running')  # running, completed, failed
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ParsingSession {self.platform} - {self.status}>"


class Manager(Base):
    """Managers who receive listings"""
    __tablename__ = 'managers'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Preferences
    city = Column(String(100))
    max_price = Column(Float)
    min_rooms = Column(Integer)

    def __repr__(self):
        return f"<Manager {self.name} - {self.telegram_id}>"


# Database connection
def init_db(db_path='rental_parser.db'):
    """Initialize database connection"""
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def get_unsent_listings(session, limit=10):
    """Get unsent listings ordered by created_at"""
    return session.query(RentalListing).filter(
        RentalListing.sent_to_manager == False,
        RentalListing.is_active == True
    ).order_by(RentalListing.created_at.desc()).limit(limit).all()


def mark_as_sent(session, listing_id, manager_id):
    """Mark listing as sent to manager"""
    listing = session.query(RentalListing).filter(
        RentalListing.id == listing_id
    ).first()

    if listing:
        listing.sent_to_manager = True
        listing.sent_at = datetime.utcnow()
        listing.manager_id = manager_id
        session.commit()
        return True
    return False
