from setuptools import setup
from setuptools import find_packages

from pydirector import Version

name = 'txLoadBalancer'
setup(
    name = name,
    version = Version,
    description = "Python Director - TCP load balancer.",
    author = "Anthony Baxter, Duncan McGreggor",
    author_email = "anthony@interlink.com.au, oubiwann@divmod.com",
    url = 'https://launchpad.net/txloadbalancer',
    packages = find_packages(),
    scripts = ['bin/pydir.py', 'bin/pydir++.py', 'bin/pydir.tac'],
    classifiers = [
       'Development Status :: 5 - Production/Stable',
       'Environment :: Web Environment',
       'Environment :: No Input/Output (Daemon)',
       'License :: OSI Approved :: Python Software Foundation License',
       'Operating System :: POSIX',
       'Operating System :: MacOS :: MacOS X',
       'Operating System :: Microsoft',
       'Programming Language :: Python',
       'Intended Audience :: System Administrators',
       'Intended Audience :: Developers',
       'Topic :: Internet',
       'Topic :: System :: Networking',
    ]

)
