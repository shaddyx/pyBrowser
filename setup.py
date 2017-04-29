from distutils.core import setup
setup(
  name = 'pyBrowser',
  packages = ['pyBrowser'],
  version = '0.2',
  description = 'simple headless browser',
  author = 'Anatolii Yakushko',
  author_email = 'shaddyx@gmail.com',
  url = 'https://github.com/shaddyx/pyBrowser', # use the URL to the github repo
  download_url = 'https://github.com/shaddyx/pyBrowser/tarball/0.1',
  keywords = ['headless', 'browser'], # arbitrary keywords
  classifiers = [],
  install_requires=[
          'ghost.py',
      ]
)
