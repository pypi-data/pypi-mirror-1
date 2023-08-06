from distutils.core import setup

version = '0.4'

setup(name='autumn',
      version=version,
      description="A minimal ORM",
      author="Jared Kuolt",
      author_email="me@superjared.com",
      url="http://autumn-orm.org",
      packages = ['autumn', 'autumn.db', 'autumn.tests'],
      )