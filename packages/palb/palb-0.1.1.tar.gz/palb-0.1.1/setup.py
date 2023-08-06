from setuptools import setup

__version__ = '0.1.1'
setup(
    name='palb',
    version=__version__,
    description='Python Apache-Like Benchmark Tool',
    long_description=open('README.txt').read() + open('CHANGELOG.txt').read(),
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
    packages=['palb', 'palb.getter'],
    zip_safe=False,
    tests_require=['nose>=0.10'],
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': [
            'palb = palb:main',
        ]
    }
)