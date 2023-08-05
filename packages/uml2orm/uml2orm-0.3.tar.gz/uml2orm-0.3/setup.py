from distutils.core import setup
#from setuptools import setup
import uml2orm

base_package = "uml2orm"
codegen = "%s/codegen" % base_package
umlparser = "%s/umlparser" % base_package

setup(
    name = base_package,
    version = uml2orm.__version__,
    description = 'uml2orm',
    author='Guilherme Polo',
    author_email = 'ggpolo@gmail.com',
    packages = [base_package, codegen, umlparser, "%s/sql" % codegen,
                "%s/orm" % codegen]            
    )
