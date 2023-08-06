from setuptools import setup, find_packages

setup(
    name = 'lanyon',
    version = 1,
    url = 'http://bitbucket.org/arthurk/lanyon/',
    license = 'BSD',
    description = 'Static Site Generator',
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

