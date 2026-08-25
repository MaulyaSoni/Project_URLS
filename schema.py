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
    owner : Mapped[str] = mapped_column(String(100))
    short_link: Mapped[str] = mapped_column(String(200))

    stats_object = relationship("Stats" , back_populates = "url_object")


class Stats(Base):
    __tablename__ = 'URL_Stats_table'

    total_clicks : Mapped[int] = mapped_column(Integer)
    clicks_per_day : Mapped[int] = mapped_column(Integer) 

    url_id : Mapped[str] = mapped_column(ForeignKey("URL_table.url_id"), primary_key=True , nullable=False)
    url_object =relationship ("URL" , back_populates = "stats_object")
