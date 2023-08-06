from setuptools import setup, find_packages

setup(
    name='zgl',
    version='0.1.3',
    packages=find_packages(
        'src',exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_dir={'':'src'},
    test_suite="test",
    install_requires = [
        'sippy-ftgl>=0.1.0',
        'PIL',
        'numpy',
        'PyOpenGL'
        ],

    # metadata for upload to PyPI
    author = "zehao chang",
    author_email = "zehao.chang@gmail.com",
    description = "OpenGL graph drawing library",
    license = "contact developer",
    keywords = "OpenGL graph node edge dependency directed",
    url = "",
    long_description = "This package is an OpenGL based library for drawing interactive graphs",
    platforms = ["All"]

)
