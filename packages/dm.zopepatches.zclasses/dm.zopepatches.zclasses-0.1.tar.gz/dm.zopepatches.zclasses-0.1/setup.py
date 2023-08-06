from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      include_package_data=True,
      namespace_packages=['dm', 'dm.zopepatches'],
      zip_safe=False,
      entry_points = dict(
        ),
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'dm', 'zopepatches', 'zclasses')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='dm.zopepatches.zclasses',
      version=pread('VERSION.txt').split('\n')[0],
      description='Through the Web application development without deep programming skills (former ZClasses functionality in the Zope core).',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 3 - Alpha',
#       'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://pypi.python.org/dm.zopepatches.zclasses',
      packages=['dm', 'dm.zopepatches', 'dm.zopepatches.zclasses'],
      keywords='application development menu web',
      license='BSD',
      **setupArgs
      )



