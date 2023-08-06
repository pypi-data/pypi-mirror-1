from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name='palb',
    version="0.0.1",
    description='Python Apache-Like Benchmark Tool',
    long_description=open('README.txt').read(),
    author='Oliver Tonnhofer',
    author_email='olt@bogosoft.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Testing :: Traffic Generation',
        'Topic :: Utilities',
      ],
    license=open('LICENSE.txt','r').read(),
    #url='',
    py_modules=['palb'],
    zip_safe=False,
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': [
            'palb = palb:main',
        ]
    }
)