from setuptools import setup

setup(
    name='whereampy',
    version='0.3',
    author='Michael Schurter',
    author_email='michael@susens-schurter.com',
    url='http://bitbucket.org/schmichael/whereampy/',
    description='Simple utility created as an example setuptools project.',
    long_description=open('README.txt').read(),
    license='Public Domain',
    packages=['whereampy'],
    package_data={
        'whereampy': ['setup.py.template'],
    },
    entry_points={
        'console_scripts': [
            'whereampy = whereampy.cli:main',
            'mkpkg = whereampy.mkpkg:main',
        ],
    },
    # The following is included as an example
    #install_requires=[
    #   'lxml >= 2.2.2, < 2.3',
    #   'psycopg2 >= 2.0, < 2.1',
    #],
)
