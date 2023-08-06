from setuptools import setup, find_packages
import os

ldesc = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
    name='arprequest',
    version='0.3',
    description=('A class which sends an ARP Request to know if a '
                    'host is online on local networks'),
    long_description=ldesc,
    keywords='arp network ethernet',
    author='Antoine Millet',
    author_email='antoine@inaps.org',
    license='WTFPL',
    py_modules=['arprequest'],
    url='http://idevelop.org/p/labo/page/ArpRequest/',
    classifiers=[
        'Topic :: Communications',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: Public Domain',
        'Operating System :: Unix',
        'Programming Language :: Python',
    ],
)
