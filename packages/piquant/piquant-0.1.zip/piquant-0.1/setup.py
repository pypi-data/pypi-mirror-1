"""
Setup script for Piquant
"""

from distutils.core import setup

version = '0.1'

description='A Python package extending NumPy and SciPy to allow specification of numbers and arrays with physical units.'

if __name__=="__main__":
    setup(name='piquant',
      version=version,
      py_modules=['piquant_unit_prefs','piquant_no_units','piquant_no_units_no_warnings'],
      packages=['piquant'],
      requires=['numpy(>=1.0.3)'],
      url='http://piquant.sourceforge.net/',
      download_url='https://sourceforge.net/project/platformdownload.php?group_id=227321',
      description=description,
      long_description=description,
      author='Dan Goodman, Romain Brette',
      author_email='dan.goodman at ens.fr',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Physics'
        ]
      )