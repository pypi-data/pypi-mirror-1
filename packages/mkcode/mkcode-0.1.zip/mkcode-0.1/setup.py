from setuptools import setup, find_packages

version = "0.1"

long_desc = file('README.txt').read()

setup(
    name='mkcode',
    version=version,
    description="A make-style Python build tool",
    long_description=long_desc,
    author="Maris Fogels",
    author_email="mfogels@gmail.com",
    url="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console"
        ],
    install_requires=[
    	#'path.py>=2.2'	# this needs to be re-packaged
        ],
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    mk=mkcode:run_mk
    """,
    test_suite='nose.collector'
)
