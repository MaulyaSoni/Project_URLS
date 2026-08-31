from sqlalchemy import Integer , String , create_engine , Column , ForeignKey
from sqlalchemy.orm import DeclarativeBase , Mapped , mapped_column , relationship

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
    secret_key : Mapped[str] = mapped_column(String(255))
    total_clicks : Mapped[int] = mapped_column(Integer , default=0)
    
    
    # clicks_per_day : Mapped[int] = mapped_column(Integer , default=0) 

