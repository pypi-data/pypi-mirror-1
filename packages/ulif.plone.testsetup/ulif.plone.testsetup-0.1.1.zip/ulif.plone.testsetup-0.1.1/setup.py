from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

tests_require = [
    'elementtree',
    ]

long_description = (
    read('README.txt')
    + '\n\n'
    + 'Detailed Documentation\n'
    + '**********************\n'
    + '\n'
    + read('src', 'ulif', 'plone', 'testsetup', 'README.txt')
    + '\n\n'
    + read('CHANGES.txt')
    + '\n\n'
    + 'Download\n'
    + '********\n'
    )

setup(
    name='ulif.plone.testsetup',
    version='0.1.1',
    author='Uli Fouquet',
    author_email='uli@gnufix.de',
    url = 'https://cheeseshop.python.org/pypi/ulif.plone.testsetup',
    description='Easier test setup for Plone 3 projects.',
    long_description=long_description,
    license='ZPL 2.1',
    keywords="plone3 plone zope test unittest doctest testsetup",
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Framework :: Plone',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['ulif', 'ulif.plone'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'z3c.testsetup'
                      ],
    tests_require = tests_require,
    extras_require = dict(test=tests_require),
)
