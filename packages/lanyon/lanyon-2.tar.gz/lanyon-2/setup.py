from setuptools import setup, find_packages

setup(
    name = 'lanyon',
    version = 2,
    url = 'http://bitbucket.org/arthurk/lanyon/',
    license = 'BSD',
    description = 'A static website generator that uses the file system structure to organize articles.',
    author = 'Arthur Koziel',

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    package_data={'lanyon': ['templates/default.html'],},
    zip_safe = False,

    # install the lanyon executable
    entry_points = {
        'console_scripts': [
            'lanyon = lanyon.app:main'
        ]
    },
    install_requires = [
        'Jinja2',
    ],
)

