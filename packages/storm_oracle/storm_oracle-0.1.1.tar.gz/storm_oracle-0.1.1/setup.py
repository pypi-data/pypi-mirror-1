from setuptools import setup, find_packages

setup(
    name='storm_oracle',
    version='0.1.1',
    packages=find_packages('src'),
    package_dir={'' : 'src'},
    install_requires=['storm', 'cx_Oracle'],
    url='https://code.launchpad.net/~jbaker/+junk/storm_oracle',
    )
