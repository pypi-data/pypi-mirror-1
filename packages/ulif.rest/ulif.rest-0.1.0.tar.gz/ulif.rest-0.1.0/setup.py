from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n\n'
    + 'Detailed Documentation\n'
    + '**********************\n'
    + '\n'
    + read('src', 'ulif', 'rest', 'README.txt')
    + '\n\n'
    + read('CHANGES.txt')
    + '\n\n'
    + 'Download\n'
    + '********\n'
    )

setup(
    name='ulif.rest',
    version='0.1.0',
    author='Uli Fouquet, parts by Georg Brandl and Lea Wiemann',
    author_email='uli@gnufix.de',
    url = 'http://pypi.python.org/pypi/ulif.rest',
    description='ReStructuredText extensions.',
    long_description=long_description,
    license='public domain, BSD, GPL',
    keywords="docutils sphinx documentation rest restructuredtext pygments",
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Other Audience',
                 'Intended Audience :: System Administrators',
                 'License :: OSI Approved :: BSD License',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'License :: Public Domain',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Topic :: Documentation',
                 'Topic :: Software Development :: Documentation',
                 'Topic :: Text Processing',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['ulif'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'docutils==0.4',
                      'Pygments',
                      ],
)
