from distutils.core import setup
import wchartype

setup (name='wchartype',
       version=wchartype.__version__,
       description=wchartype.__description__,
       author=wchartype.__author__,
       py_modules=["wchartype"])