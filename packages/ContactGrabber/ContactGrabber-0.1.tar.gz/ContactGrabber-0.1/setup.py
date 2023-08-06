from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="ContactGrabber",
      version="0.1",
      packages=find_packages(),
      description="Grabs contacts from GMail, Yahoo!, Rediff etc.",
      long_description="""
Grabs contacts from GMail, Yahoo!, Rediff etc.
How to use:

from contactgrabber import grab_contacts
try:
    emails = grab_contacts('mike', 'password_of_mike', 'rediff')
    if len(emails) == 0:
        print 'No contacts found. Did you enter invalid user ID / pasword?'
    print str(emails)
except:
    print 'Invalid UserID/Password'

Currently supported sitenames: 'rediff', 'gmail', 'yahoo'
""",
      install_requires=[],
      author="Sanjay",
      author_email="skpatel20@gmail.com",
      maintainer="Ranjan",
      maintainer_email="ranjan.naik@gmail.com")