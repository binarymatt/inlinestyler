from setuptools import setup, find_packages

setup(name="inlinestyle",
      version="0.4",
      description="convert html style blocks to inline style statements",
      author="Matt George",
      packages=find_packages('src', exclude=['tests']),
      package_dir={'': 'src'},
      author_email="mgeorge@gmail.com",
      install_requires=["beautifulsoup4", "nose", "cssutils"])
