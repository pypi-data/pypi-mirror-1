try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

setup(name = "django-ldapbackend",
    version = "0.0.1.1",
    description = "LDAP Backend for Django (1.0 or higher)",
    long_description = """A simple LDAP Backend for Django installed globally because it uses settings.py to store everything and is a modular plugin.""",
    author = "Alexander 'Swixel' Stanley",
    author_email = "lexi@swixel.net",
    url = "http://django-ldapbackend.googlecode.com",
    download_url = "http://django-ldapbackend.googlecode.com/files/django-ldapbackend-0.0.1.tar.gz",
    packages=find_packages(exclude='tests'),
    #package_data={'': '*.txt'},
    install_requires=['Django>=1.0', 'python-ldap>=2.3.9'],
    license = 'New BSD',
    platforms = 'Windows, POSIX',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Office/Business',
        'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP',
    ],
) 
