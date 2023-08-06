
from setuptools import setup

version = 1.4

DESCRIPTION = "Skimpy Gimpy Audio/visual Tools"
LONG_DESCRIPTION = """\
Skimpy is a tool for generating HTML visual, PNG visual,
and WAVE audio representations for strings which people can
understand but which web robots and other computer programs
will have difficulty understanding. Skimpy is an example of
a Captcha: an acronym for "Completely Automated Public Turing
test to tell Computers and Humans Apart".
"""

setup(
   name="skimpyGimpy",
   version=version,
   author="Aaron Watters",
   author_email="aaronwmail-sourceforge@yahoo.com",
   url="http://skimpygimpy.sourceforge.net/",
   description=DESCRIPTION,
   long_description=LONG_DESCRIPTION,
   download_url="http://skimpygimpy.googlecode.com/files/skimpyGimpy-1.3-py2.4.egg",
   license="",
   packages=["skimpyGimpy"],
   platforms="Python 2.4 +",
   classifiers=[
       "Topic :: Multimedia :: Sound/Audio",
       "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
       "Topic :: Multimedia :: Sound/Audio :: Speech",
       ]
   )
