from sqlalchemy import Integer , String , UniqueConstraint , create_engine , Column , ForeignKey , Sequence , Date , DateTime 
from sqlalchemy.orm import DeclarativeBase , Mapped , mapped_column , relationship
from datetime import datetime 

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'User_table'

    userid : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username : Mapped[str] = mapped_column(String(20) , nullable = False)
    email: Mapped[str] = mapped_column(String(255) , unique= True ,nullable=False)
    hashed_password : Mapped[str] = mapped_column(String(100) , nullable = False)
    user_role : Mapped[str] = mapped_column(String(20), nullable = False)

class URL(Base):
    __tablename__ = 'URL_table'
    
    url_id: Mapped[int] = mapped_column(Integer , primary_key=True , autoincrement=True)
    url : Mapped[str] = mapped_column(String(500))
    owner_id : Mapped[int] = mapped_column(Integer)
    short_link: Mapped[str] = mapped_column(String(200))
    total_clicks : Mapped[int] = mapped_column(Integer , default=0)

    analytics  = relationship("URLStats" , back_populates = "url_obj")
    logs = relationship("ClickLog" , back_populates = "url_obj")

class URLStats(Base):
    __tablename__ = 'URL_Stats_table'
    
    stats_id : Mapped[int] = mapped_column(Integer , autoincrement=True , primary_key=True)
    url_id : Mapped[int] = mapped_column(Integer , ForeignKey("URL_table.url_id"),nullable=False)    
    date : Mapped[date] = mapped_column(Date , nullable= False)
    clicks_per_day : Mapped[int] = mapped_column(Integer , default=0) 

    url_obj = relationship("URL" , back_populates="analytics")

class ClickLog(Base):
    __tablename__ = 'ClickLog_table'
    log_id : Mapped[int] = mapped_column(Integer , autoincrement=True , primary_key=True)
    url_id : Mapped[int] = mapped_column(Integer , ForeignKey("URL_table.url_id") , nullable=False)    
    clicked_at : Mapped[datetime] = mapped_column(DateTime , nullable= False)
    
    url_obj = relationship("URL" , back_populates="logs")
