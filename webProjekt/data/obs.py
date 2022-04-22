import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Obs(SqlAlchemyBase):
    __tablename__ = 'obs'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    news_id = sqlalchemy.Column(sqlalchemy.Integer)
