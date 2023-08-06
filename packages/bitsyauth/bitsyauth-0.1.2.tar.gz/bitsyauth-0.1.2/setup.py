from setuptools import setup, find_packages

version = '0.1.2'

setup(name='bitsyauth',
      version=version,
      description="form + digest auth middleware",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='auth',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/bitsyauth',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['Paste',
                        'PasteScript',
                        'markup', # TO DEPRECATE
                        'skimpygimpy',
                        ],
      dependency_links=[
                        'http://svn.pythonpaste.org/Paste/trunk#egg=Paste',
                        ],
      entry_points="""
              
      """,
      )
