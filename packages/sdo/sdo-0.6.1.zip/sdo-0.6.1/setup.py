try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

description = """\
example of usage:

import cx_Oracle
import sdo
conn=cx_Oracle.connect("scott/tiger")
cur=conn.cursor()
cur.execute("select geometry from city")
print sdo.Geometry(cur.fetchone()[0]).wkt()
""" 

setup(
    name='sdo',
    version="0.6.1",
    summary = "Converts oracle SDO_GEOMETRY objects to WKT and GeoJSON.",
    description= description,
    author='tib00r',
    author_email='tibor.arpas@infinit.sk',
    #url='',
    install_requires=["python-nicefloat"],
    classifiers="Development Status :: 4 - Beta",
    py_modules=['sdo','testsdo'],
    include_package_data=True
)
