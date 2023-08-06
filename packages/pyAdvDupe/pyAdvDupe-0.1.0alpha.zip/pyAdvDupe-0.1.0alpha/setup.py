from distutils.core import setup

setup(name='pyAdvDupe',
      version='0.1.0alpha',
      description='Python library to parse and write Gmod Advanced Duplicator data files',
      author='sk89q',
      author_email='the.sk89q@gmail.com',
      license='GPLv2',
      url='http://github.com/sk89q/pyadvdupe',
      packages=['advdupe'],
      package_dir={'advdupe': 'src/advdupe'}
      )
