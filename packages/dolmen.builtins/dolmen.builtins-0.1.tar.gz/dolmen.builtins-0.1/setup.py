from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.builtins'
version = '0.1'
readme = open(join('src', 'dolmen', 'builtins', "README.txt")).read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = name,
      version = version,
      description = 'Zope interfaces applied to Python builtins',
      long_description = readme + '\n\n' + history,
      keywords = 'Zope3 Dolmen Builtins',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org',
      download_url = 'http://pypi.python.org/pypi/dolmen.builtins',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = True,
      install_requires=[
          'setuptools',
          'zope.interface'
      ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
