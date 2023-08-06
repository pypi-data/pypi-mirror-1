from setuptools import setup, find_packages

setup(
    name='cloudpool',
    version='0.1.2',
    packages=find_packages(
        'src',exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_dir={'':'src'},
    test_suite='test',
    tests_require= ['simplejson>=2.0.9'],
    install_requires = [
        'paramiko>=1.7.6',
        'threadpool>=1.2.7'
        ],

    # metadata for upload to PyPI
    author = "michael j pan",
    author_email = "mikepan@gmail.com",
    description = "pool of execution hosts",
    license = "New BSD",
    keywords = "cloud pool execute",
    url = "http://code.google.com/p/cloudpool/",
    long_description = "This Python library enables one to create a pool of processors for executing processes. Hosts can be added to and removed from the pool.",
    platforms = ["All"]

)
