from setuptools import setup, find_packages

setup (
    name = 'stxnext.log',
    version = '0.2.0',
    author = 'STX Next Sp. z o.o, Wojciech Lichota',
    author_email = 'info@stxnext.pl, wojciech.lichota@stxnext.pl',
    description = 'This logger offers some conveniences that make easier of logging from python code and from ZPT templates.',
    long_description = open('README.txt').read(),
    keywords = 'python log logger',
    platforms = ['any'],
    url = 'http://stxnext.pl/open-source/stxnext.log',
    license = 'Zope Public License, Version 2.1 (ZPL)',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['stxnext'],
    zip_safe = False,
    install_requires = ['setuptools'],
    
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Zope2',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )