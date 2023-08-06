from distutils.core import setup
from src import __version__

setup(name='autumn',
      version=__version__,
      description="A minimal ORM",
      author="Jared Kuolt",
      author_email="me@superjared.com",
      url="http://autumn-orm.org",
      packages = ['src', 'src.db', 'src.tests'],
      )