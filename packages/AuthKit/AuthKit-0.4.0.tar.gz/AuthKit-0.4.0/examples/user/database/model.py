from sqlalchemy import *
from sqlalchemy.ext.assignmapper import assign_mapper
from sqlalchemy.ext import sessioncontext

meta = MetaData()
engine = create_engine('sqlite:///test.db')
meta.connect(engine)

def make_session(uri=None, echo=None, session_kwargs=None, **kwargs):
    if session_kwargs is None:
        session_kwargs = {}
    return create_session(bind_to=engine, **session_kwargs)

ctx = sessioncontext.SessionContext(make_session)

# You would add any custom SQLAlchmy models or tables here