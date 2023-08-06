from setuptools import setup

setup(
	version = "0.4.1",
	description = "Toolserver Framework for Python",
	author = "Georg Bauer",
	author_email = "gb@rfc1437.de",
	url = "http://bitbucket.org/rfc1437/toolserver/",
	name='Toolserver', 
	long_description=file("README").read(),
	license='MIT/X',
	platforms=['BSD','Linux','MacOS X', 'win32'],
	packages=['Toolserver'],
    scripts=['tsctl', 'tsctl-win32.py'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    install_requires = ['medusa'],
)
