from distutils.core import setup

setup(name='pOFCy',
      version='0.1',
      description="Python library for Open Flash Chart",
      long_description="pOFCy is handy python (version 3.x) library to generate Open Flash Chart 2 JSON configuration data.",
      classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Internet",
      ],
      keywords='flash graphics charts json visualisation visualization internet ofc2',
      author='Eugene Chernyshov',
      author_email='Chernyshov.Eugene@gmail.com',
      url='http://code.google.com/p/pofcy/',
      license='LGPL',
      packages=['ofc2'],
      )