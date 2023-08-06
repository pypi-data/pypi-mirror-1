from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n\n'
    + read('SPONSORS.txt')
    + '\n\n'
    + read('CHANGES.txt')
    + '\n\n'
    + 'Download\n'
    + '********\n'
    )

setup(
    name='psj.site',
    version='0.1',
    author='Uli Fouquet',
    author_email='uli@gnufix.de',
    url = 'http://pypi.python.org/pypi/psj.site',
    description='Plone Scholarly Journal - the site setup',
    long_description=long_description,
    license='GPL',
    keywords="zope site scholarly scholar journal plone plone3",
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Framework :: Zope2',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['psj'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'elementtree',
                      'ulif.plone.testsetup',
                      'lxml',
                      'psj.policy',
                      'psj.content',
                      'Products.ATVocabularyManager',
                      'Products.membrane',
                      'Products.FacultyStaffDirectory',
                      'Products.LinguaPlone',
                      ],
    entry_points="""
    # -*- Entry points: -*-
    [console_scripts]
    ooo_convert = psj.policy.bin.ooo_convert:main
    """,

)
