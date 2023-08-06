try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='sdo',
    version="0.6.0",
    #description='',
    author='tib00r',
    author_email='tibor.arpas@infinit.sk',
    #url='',
    install_requires=["python-nicefloat"],
    py_modules=['sdo','testsdo'],
    include_package_data=True
)
