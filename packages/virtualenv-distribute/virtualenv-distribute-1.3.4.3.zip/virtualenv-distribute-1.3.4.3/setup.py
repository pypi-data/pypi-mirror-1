try:
    from distribute import setup
except ImportError:
    from distutils.core import setup
    print 'Note: without Setuptools installed you will have to use "python -m virtualenv ENV"'
import sys, os

version = '1.3.4.3'

f = open(os.path.join(os.path.dirname(__file__), 'docs', 'index.txt'))
long_description = f.read().strip()
f.close()

setup(name='virtualenv-distribute',
      version=version,
      description="Virtual Python Environment builder",
      long_description=long_description,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
      ],
      keywords='distribute setuptools deployment installation distutils',
      author='Florian Schulze',
      author_email='florian.schulze@gmx.net',
      url='http://bitbucket.org/fschulze/virtualenv-distribute/',
      license='MIT',
      py_modules=['virtualenv'],
      ## Hacks to get the package data installed:
      packages=[''],
      package_dir={'': '.'},
      package_data={'': ['support-files/*-py%s.egg' % sys.version[:3]]},
      zip_safe=False,
      entry_points="""
      [console_scripts]
      virtualenv = virtualenv:main
      """,
      )
