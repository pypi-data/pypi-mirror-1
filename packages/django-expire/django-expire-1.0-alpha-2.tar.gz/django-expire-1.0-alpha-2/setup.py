#!/usr/bin/env python
from distutils.core import setup
from django_expire import get_version


def read_files(*filenames):
    """
    Output the contents of one or more files to a single concatenated string.

    """
    output = []
    for filename in filenames:
        f = open(filename)
        try:
            output.append(f.read())
        finally:
            f.close()
    return '\n'.join(output)


setup(
    name='django-expire',
    version=get_version(join='-'),
    url='http://bitbucket.org/smileychris/django-expire',
    download_url='http://bitbucket.org/smileychris/django-expire/downloads',
    description='Django authentication-based session expiration',
    long_description=read_files('README'),
    author='Chris Beaven',
    author_email='smileychris@gmail.com',
    platforms=['any'],
    packages=[
        'django_expire',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
