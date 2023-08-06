from setuptools import setup, find_packages

setup(name="clixevolve",
    version="0.1dev",
    description="ClixEvolve -- the righteous schema evolver",
    long_description="""ClixEvolver will evolve any MySQL schema, 'guaranteed'.""",
    author="Silas Snider",
    author_email="silas.snider@showclix.com",
    url="http://silassnider.com",
    packages=find_packages(exclude='tests'),
    package_data={'': ['*.dist']},
    install_requires=['argparse', 'pyyaml'],
    entry_points={
        'console_scripts': [
#            'clixevolve = clixevolve.migrate:main()',
            'clixextract = clixevolve.extract_structure:main',
            'clixdiff = clixevolve.diff:main'
        ]
    }
)