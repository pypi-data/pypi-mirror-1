from distutils.core import setup

VERSION = '0.1'

setup(name='eventbrite',
      version=VERSION,
      author="Josh Toft",
      author_email='josh@fwix.com',
      description='A client for the Eventbrite API.',
      license='MIT',
      long_description="""
    A client for Eventbrite's API (http://www.eventbrite.com/).

    Uses httplib2 and simplejson.
      """,
      py_modules=['eventbrite'],
      classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries'
        ])
