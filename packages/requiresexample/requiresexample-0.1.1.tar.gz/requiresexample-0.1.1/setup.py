from distutils.core import setup
import requiresexample

README = open('README.txt').read()
desc, long_desc = README.split('\n', 1)

setup(name="requiresexample",
      version=requiresexample.__version__,
      description=desc,
      long_description=long_desc,
      author='srid',
      author_email='sridhar.ratna@gmail.com',
      url='http://activestate.com/activepython',
      
      packages=['requiresexample'],
      requires=['lxml',  'httplib2'],
      )

      
