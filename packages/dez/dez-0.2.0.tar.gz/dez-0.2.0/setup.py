from setuptools import setup, find_packages
import os

setup(
    name='dez',
    version='0.2.0',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    url='http://www.orbited.org/svn/dez',
#    download_url='http://www.orbited.org/download',
    license='MIT License',
    description='A set of pyevent-based network services, including a WSGI server',
    long_description='This package implements various network and server clients using the rel network library. It will attempt to use pyevent (libevent wrapper) or epoll for high performance before falling back to either poll or select for compatability. All dependancies are pure-python and can be installed with easy_install.',
    packages=[
        'dez',
        'dez.http',
        'dez.http.server',
        'dez.http.client',
        'dez.http.proxy',
        'dez.stomp',
        'dez.stomp.server',
        'dez.op',
        'dez.op.server',
        'dez.network',
        'dez.samples'
    ],
    zip_safe = False,
    install_requires = [
        "rel>=0.1.5",
    ],

    entry_points = '''
        [console_scripts]
        dez_test = dez.samples.test:main
    ''',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
