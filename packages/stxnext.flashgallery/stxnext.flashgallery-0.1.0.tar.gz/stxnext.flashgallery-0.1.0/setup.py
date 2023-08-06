from setuptools import setup, find_packages

setup (
    name = 'stxnext.flashgallery',
    version = '0.1.0',
    author = 'STX Next Sp. z o.o, Wojciech Lichota',
    author_email = 'info@stxnext.pl, wojciech.lichota@stxnext.pl',
    description = 'Integration of SimpleViewer and AutoViewer photo galleries with Plone.',
    long_description = open('README.txt').read(),
    keywords = 'python plone gallery photo flash',
    platforms = ['any'],
    url = 'http://stxnext.pl/open-source/stxnext.flashgallery',
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
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Programming Language :: Python',
        ]
    )