from setuptools import setup

from chouwa import __version__

setup(
    name='chouwa',
    version='.'.join(str(bit) for bit in __version__),
    url='http://bitbucket.org/trevor/chouwa',
    description='Django & Jinja2 integration',
    author='Trevor Caira',
    author_email='trevor@caira.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=['chouwa'],
)
