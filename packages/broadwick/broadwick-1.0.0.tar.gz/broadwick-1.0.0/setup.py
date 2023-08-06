from setuptools import setup, find_packages
import os

base_dir = os.path.dirname(__file__)

setup(name='broadwick', 
      version='1.0.0',
      description="A Python Application Environment.",
      author='Peter Bunyan, Jonathan Marshall, Petra Chong',
      long_description=open(os.path.join(base_dir,'docs','description.txt')).read(),
      url='http://launchpad.net/broadwick',
      packages = find_packages(),
      package_data = {
        '' : ["*.genshi", "*.css", "*.conf"], 
        },
      install_requires = [
        'PyDispatcher',
        'twisted >=8.0.1',
        'SQLAlchemy >= 0.5.2',
        ],
      entry_points = {
        'console_scripts' : [
            'broadwick_appserver = appserver.dashboard.main:main',
            'broadwick_supervisor_conf = appserver.scripts.setup_supervisor:main',
            'broadwick_supervisor_startall = appserver.scripts.startup_all:main',
            'broadwick_supervisor_proxy = appserver.scripts.sproxy:main',
            'broadwick_mail = broadwick.utils.mail:main',
            'broadwick_archive = appserver.scripts.file_zipper:main',
            ]
        }
      )

