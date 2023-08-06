from setuptools import setup, find_packages
import os

setup(
    name='dez',
    version='0.2.4',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    url='http://www.orbited.org/svn/dez',
#    download_url='http://www.orbited.org/download',
    license='MIT License',
    description='A set of pyevent-based network services',
    long_description='',
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
        # "event >= 0.3"
    ],

    entry_points = '''
        [console_scripts]
        dez_test = dez.samples.test:main
        dbench = dez.samples.http_load_test:main
        [paste.server_runner]
        wsgi_server = dez.http.application:serve_wsgi_application
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
