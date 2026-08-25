from sqlalchemy import Integer , String , create_engine , Column 
from sqlalchemy.orm import DeclarativeBase , Mapped , mapped_column

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'User_table'

    userid : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username : Mapped[str] = mapped_column(String(20) , nullable = False)
    email: Mapped[str] = mapped_column(String(255) , unique= True ,nullable=False)
    hashed_password : Mapped[str] = mapped_column(String(100) , nullable = False)
    user_role : Mapped[str] = mapped_column(String(20), nullable = False)

class Url_stats(Base):
    __tablename__ = 'Url_stats_table'

    url : Mapped[str] = mapped_column(String(500), primary_key=True)
    short_link: Mapped[str] = mapped_column(String(200))
    total_clicks : Mapped[int] = mapped_column(Integer)
    clicks_per_day : Mapped[int] = mapped_column(Integer) 