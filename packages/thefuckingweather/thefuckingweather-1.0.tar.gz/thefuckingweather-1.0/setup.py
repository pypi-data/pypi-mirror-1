from distutils.core import setup
import thefuckingweather

setup(name="thefuckingweather",
      version="1.0",
      description="Python API for The Fucking Weather",
      author="Ian Weller",
      author_email="ian@ianweller.org",
      url="http://ianweller.org/thefuckingweather",
      py_modules=["thefuckingweather"],
      license="WTFPL",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Intended Audience :: End Users/Desktop",
          "License :: Freely Distributable",
          "Operating System :: OS Independent",
          "Topic :: Utilities",
      ]
     )
