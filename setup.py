from setuptools import setup

setup(
    name='a9tools',
    version='0.1.0',
    author='Marius Kaufmann',
    author_email='marius.kaufmann@googlemail.com',
    packages=['a9tools'],
    scripts=['bin/a9tools'],
    url='https://www.dasug.de', # don't really have a website for this right now
    license='LICENSE',
    description='library to deal with a-train 9 data files',
    install_requires=[],
)