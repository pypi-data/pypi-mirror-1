from setuptools import setup, find_packages

setup (
    name = 'stxnext.pdb',
    version = '0.2.1',
    author = 'STX Next Sp. z o.o, Wojciech Lichota',
    author_email = 'info@stxnext.pl, wojciech.lichota@stxnext.pl',
    description = 'This is extended Python Debugger (pdb). It offers few very useful features that helps in debugging, especially zope2/zope3/plone instances.',
    long_description = open('README.txt').read(),
    keywords = 'python debug debugger pdb',
    platforms = ['any'],
    url = 'http://stxnext.pl/open-source/stxnext.pdb',
    license = 'Zope Public License, Version 2.1 (ZPL)',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['stxnext'],
    zip_safe = False,
    install_requires = ['setuptools', 'stxnext.log'],
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Zope2',
        'Framework :: Zope3',
        'Framework :: Plone',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )