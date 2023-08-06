from setuptools import setup, find_packages
import os

version = '1.0.1'
name = 'enfold.recipe.patch'
namespace_packages = ['.'.join(name.split('.')[:1]),
                      '.'.join(name.split('.')[:2])]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name=name,
      version=version,
      description="zc.buildout recipe for applying patches to a buildout tree.",
      long_description= (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read(*(name.split('.') + ['README.txt']))
        + '\n' +
        'Download\n'
        '***********************\n'
        ),
      classifiers=[
       'Framework :: Buildout',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: GNU General Public License (GPL)',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='development buildout recipe',
      author='Sidnei da Silva',
      author_email='sidnei@enfoldsystems.com',
      url='http://cheeseshop.python.org/pypi/%s' % name,
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=namespace_packages,
      include_package_data=True,
      zip_safe=False,
      install_requires = ['zc.buildout', 'setuptools'],
      tests_require = ['zope.testing'],
      test_suite = '%s.tests.test_suite' % name,
      entry_points = { 'zc.buildout' : ['default = %s:Recipe' % name] },
      )
