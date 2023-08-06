from setuptools import setup, find_packages
setup(
    name = "zamtools-navigation",
    version = '1.0',
    description = "Django application for displaying and tracking site navigation",
    author = "Ian Zamojc",
    author_email = "zamtools@zamtools.com",
    url = "http://code.google.com/p/zamtools-navigation/",
    packages = [
        'navigation',
    ],
    zip_safe = False,
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
