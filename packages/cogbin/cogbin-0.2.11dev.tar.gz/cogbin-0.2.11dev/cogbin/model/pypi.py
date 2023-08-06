from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, Index
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from cogbin.model import DeclarativeBase, metadata, DBSession

class PyPIPackages(DeclarativeBase):
    __tablename__ = 'pypi_packages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode,nullable=False, index=True)
    version = Column(Unicode)
    maintainer = Column(Unicode)
    maintainer_email = Column(Unicode)
    author = Column(Unicode)
    author_email = Column(Unicode)
    platform = Column(Unicode)
    keywords = Column(Unicode)
    description = Column(Unicode)
    download_url = Column(Unicode)
    summary = Column(Unicode)
    home_page = Column(Unicode)
    classifiersc = Column(Unicode)
    requires = Column(Unicode)
    full_metadata = Column(Text)

Index('UK_pypi_packages', PyPIPackages.name, PyPIPackages.version, unique=True)

