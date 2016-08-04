from setuptools import setup

# See PEP 0440: https://www.python.org/dev/peps/pep-0440/#version-scheme
# Consider making this the same as the last tagged release version
VERSION = '0.1.0'

setup(
    name='zachopy',
    version=VERSION,
    package_dir={'zachopy': '.',
                 'zachopy.borrowed': 'borrowed',
                 'zachopy.displays': 'displays',
                 'zachopy.relations': 'relations'},
    packages=['zachopy', 'zachopy.borrowed', 'zachopy.displays', 'zachopy.relations'],
    description="Various tools used in lots of code written by Zach Berta-Thompson (zkbt@mit.edu)",
    author='Zach Berta-Thompson',
    author_email='zkbt@mit.edu',
    url='https://github.com/zkbt/zachopy',
    install_requires=['numpy', 'astropy', 'astroquery', 'matplotlib', 'scipy', 'pyds9==1.8.1', 'colormath', 'parse'],
    dependency_links=['git+https://github.com/ericmandel/pyds9.git#egg=pyds9-1.8.1']
    # Uncomment this if there's a tagged release that's the same as VERSION
    # download_url = 'https://github.com/zkbt/zachopy/tarball/{}'.format(VERSION),
)
