from distutils.core import setup
setup(name='emusic',
      version='0.6',
      py_modules=['emusic'],
      scripts=["dlm.py"],
      author="Asheesh Laroia",
      author_email="asheesh@asheesh.org",
      maintainer="Asheesh Laroia",
      maintainer_email="asheesh@asheesh.org",
      description="A simple desktop interface for interacting with the eMusic.com web music service, including a feature to create a NetFlix-like download queue",
      classifiers=[
                'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
#      url="http://www.asheesh.org/something",
      )
