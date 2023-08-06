from setuptools import setup
from autorm import version

version = '.'.join([str(x) for x in version])

setup(name='autorm',
      version=version,
      description="A minimal ORM",
      author="Nino Walker",
      author_email="nino@urbanmapping.com",
      url="http://github.com/umidev/autorm",
      packages = ['autorm', 'autorm.db', 'autorm.tests'],
      package_data = {
        '': ['*.sql'],
    }

      )
