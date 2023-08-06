from os.path import abspath, dirname, join
try:
  # try to use setuptools
  from setuptools import setup
  setupArgs = dict(
      install_requires=['dm.reuse',],
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False, # to let the tests work
      )
except ImportError:
  # use distutils
  from distutils import setup
  setupArgs = dict(
    )

cd = abspath(dirname(__file__))
pd = join(cd, 'Products', 'TrustedExecutables')

def pread(filename, base=pd): return open(join(base, filename)).read().rstrip()

setup(name='Products.TrustedExecutables',
      version=pread('VERSION.txt').split('\n')[0],
      description='Trusted Zope 2 executables (scripts, templates) -- unrestricted by Zope 2 security. For Zope 2.11 and above',
      long_description=pread('README.txt'),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Framework :: Zope2',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        ],
      author='Dieter Maurer',
      author_email='dieter@handshake.de',
      url='http://www.dieter.handshake.de/pyprojects/Zope',
      packages=['Products', 'Products.TrustedExecutables',],
      keywords='Zope 2, trusted, executables, unrestricted, security ',
      license='BSD (see "dm/reuse/LICENSE.txt", for details)',
      **setupArgs
      )



