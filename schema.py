from sqlalchemy import Integer , String , create_engine , Column 
from sqlalchemy.orm import DeclarativeBaseClass , Mapped , mapped_column 

class Base(DeclarativeBaseClass):
    pass

class Users(Base):
    __tablename__ = 'User_table'

    userid : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username : Mapped[str] = mapped_column(String(20) , nullable = False)
    hashed_password : Mapped[str] = mapped_column(String(100) , nullable = False)
    user_role : Mapped[str] = mapped_column(String(20), nullable = False)

class Url_stats(Base):
    __tablename__ = 'url_stats_table'

    url : Mapped[str] = mapped_column(String)
    short_link: Mapped[str] = mapped_column(String)
    total_clicks : Mapped[int] = mapped_column(Integer)
    clicks_per_day : Mapped[int] = mapped_column(Integer)