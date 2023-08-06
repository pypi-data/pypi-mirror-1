import sqlalchemy as sa
from sqlalchemy.ext import declarative

Base = declarative.declarative_base()
metadata = Base.metadata


class User(Base):
    """A user.

      >>> u = User()
    """

    __tablename__ = 'users'

    username = sa.Column(sa.String, primary_key=True)
    password = sa.Column(sa.String)
    email = sa.Column(sa.String)


class Distro(Base):
    """A project distribution.

      >>> d = Distro()
    """

    __tablename__ = 'distros'

    distro_id = sa.Column(sa.String, primary_key=True)
    name = sa.Column(sa.String)
    owner = sa.Column(sa.String)
    author_email = sa.Column(sa.String)
    classifiers = sa.Column(sa.String)
    description = sa.Column(sa.String)
    download_url = sa.Column(sa.String)
    home_page = sa.Column(sa.String)
    keywords = sa.Column(sa.String)
    license = sa.Column(sa.String)
    metadata_version = sa.Column(sa.String)
    platform = sa.Column(sa.String)
    summary = sa.Column(sa.String)
    version = sa.Column(sa.String)
