from sqlalchemy import *

from zblog.database import engine as db

"""application table metadata objects are described here."""

users = Table('users', db, 
    Column('user_id', Integer, primary_key=True),
    Column('user_name', String(30), nullable=False),
    Column('fullname', String(100), nullable=False),
    Column('password', String(30), nullable=False),
    Column('groupname', String(20), nullable=False),
    )

blogs = Table('blogs', db, 
    Column('blog_id', Integer, primary_key=True),
    Column('owner_id', Integer, ForeignKey('users.user_id'), nullable=False),
    Column('name', String(100), nullable=False),
    Column('description', String(500))
    )
    
posts = Table('posts', db,
    Column('post_id', Integer, primary_key=True),
    Column('blog_id', Integer, ForeignKey('blogs.blog_id'), nullable=False),
    Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
    Column('datetime', DateTime, nullable=False),
    Column('headline', String(500)),
    Column('summary', String),
    Column('body', String),
    )
    
topics = Table('topics', db,
    Column('topic_id', Integer, primary_key=True),
    Column('keyword', String(50), nullable=False),
    Column('description', String(500))
   )
  
topic_xref = Table('topic_post_xref', db, 
    Column('topic_id', Integer, ForeignKey('topics.topic_id'), nullable=False),
    Column('is_primary', Boolean, nullable=False),
    Column('post_id', Integer, ForeignKey('posts.post_id'), nullable=False)
   )

comments = Table('comments', db, 
    Column('comment_id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False),
    Column('post_id', Integer, ForeignKey('posts.post_id'), nullable=False),
    Column('datetime', DateTime, nullable=False),
    Column('parent_comment_id', Integer, ForeignKey('comments.comment_id')),
    Column('subject', String(500)),
    Column('body', String),
    )
    
def create_tables():
    """creates all application tables, used when the application is run for the
    first time."""
    users.create()
    blogs.create()
    posts.create()
    topics.create()
    topic_xref.create()
    comments.create()