from setuptools import setup, find_packages

version_tuple = __import__('pascut').VERSION

if version_tuple[2] is not None:
    version = "%d.%d.%s" % version_tuple
else:
    version = "%d.%d" % version_tuple[:2]

dependencies = ['plugpy >= 0.2.1', 'werkzeug >= 0.5']

setup(
    name = "pascut",
    version = version,
    url = 'http://bitbucket.org/mopemope/pascut/',
    author = 'yutaka.matsubara',
    author_email = 'yutaka.matsubara@gmail.com',
    maintainer = 'yutaka.matsubara',
    maintainer_email = 'yutaka.matsubara@gmail.com',
    license='MIT License',
    description = 'Automation Flash build tool',
    platforms = ['Any'],
    install_requires = dependencies,
    include_package_data = True,
    packages = find_packages(),
    package_data = {'pascut': ['plugins/*.py', 'plugins/js/*.js',  ],},
    entry_points = {
            'console_scripts': [
                'pascut = pascut.main:main'
                ]
            },
    classifiers = [
       "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python"
        ]
)
