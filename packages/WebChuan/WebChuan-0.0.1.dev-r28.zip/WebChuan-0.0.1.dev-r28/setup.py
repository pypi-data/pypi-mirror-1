import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name="WebChuan",
      version="0.0.1",
      description="Library and tools for getting and parsing web",
      long_description="""""",
      author="Victor Lin",
      author_email="bornstub@gmail.com",
      url="http://webchuan.ez2learn.com",
      license = "MIT License",
      zip_safe=False,
      install_requires = [
          "Twisted",
          "lxml"
      ],
      packages=find_packages('lib'),
      package_dir = {'':'lib'},
      long_description = """
WebChuan is a set of open source libraries and tools for getting and parsing web pages of website. It is written in Python, based on Twisted and lxml.
It is inspired by GStreamer. WebChuan is designed to be back-end of web-bot, it is easy to use, powerful, flexible, reusable and efficient. 
"""   ,
      classifiers=[
          "Development Status :: 1 - Planning",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ],
)
