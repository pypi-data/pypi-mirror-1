from setuptools import setup, find_packages
setup(
    name = 'django-vcs-watch',
    version = '0.1.0',
    description = 'RSS proxy for different VCS/DVCS.',
    keywords = 'django apps svn',
    license = 'New BSD License',
    author = 'Alexander Artemenko',
    author_email = 'svetlyak.40wt@gmail.com',
    url = 'http://github.com/svetlyak40wt/django-vcs-watch/',
    install_requires = [],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages_dir = ['src'],
    packages = find_packages(),
    include_package_data = True,
)


