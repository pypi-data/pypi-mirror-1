try:
    from setuptools import setup, find_packages, Extension
except ImportError:
    print 'You need to install setuptools to install this package.'

packages = find_packages()

setup(
    name = "fibra",
    version = "0.0.9",
    packages = packages,
    url = "http://code.google.com/p/fibra/",
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    license='MIT',
    platforms=['Any'],
    description="""A package which provides advanced cooperatve concurrency using Python generators.
    """,
)

