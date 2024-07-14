from setuptools import setup, find_packages

setup(
    name='nceiDatabaseConnector',
    version='0.1.0',
    author='Fabian Klug, Tilmann Diepenbruck',
    description='A package that allows downloading and modifying GHCN-Daily Data from the NCEI Database',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tdiepenb/ESDP1-Database-Project',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "pandas",
        "requests",
        "psycopg2-binary",
    ],
)
