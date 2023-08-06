from setuptools import setup, find_packages

setup(name="clixbuild",
    version="1.2.3",
    description="ClixBuild, here to make your troubles vanish, your teeth whiter, and your .htaccess problem disappear",
    long_description="""ClixBuild, the glorified preprocessor""",
    author="Silas Snider",
    author_email="silas.snider@showclix.com",
    url="http://silassnider.com",
    packages=find_packages(exclude='tests'),
    package_data={'': ['*.dist', '.clixbuild']},
    install_requires=['Jinja2', 'argparse', 'pyyaml'],
    entry_points={
        'console_scripts': [
            'clixbuild = clixbuild.build:main'
        ]
    }
)
