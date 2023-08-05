
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    try:
        from ez_setup import use_setuptools
    except ImportError:
        print "can't find ez_setup"
        print "try: wget http://peak.telecommunity.com/dist/ez_setup.py"
        sys.exit(1)
    use_setuptools()
    from setuptools import setup, find_packages


version = '0.1.1'

setup(
    name="gitlsfiles",
    version=version,
    author="Yannick Gingras",
    author_email="ygingras@ygingras.net",
    url="",
    description="setuptools integration for Git",
    license="GPL v3 or later",
    classifiers=[
        "Topic :: Software Development :: Version Control"
        ],
    py_modules=["gitlsfiles"],
    entry_points="""
	[setuptools.file_finders]
	git=gitlsfiles:gitlsfiles
	"""
)
