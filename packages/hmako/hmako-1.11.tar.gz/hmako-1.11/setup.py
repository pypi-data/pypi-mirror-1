from setuptools import setup, find_packages

version = '1.11'

setup(name='hmako',
      version=version,
      description="a hack version mako(0.24) for html",
      keywords='wsgi myghty mako',
      author='zsp',
      author_email='zsp007@gmail.com',
      license='MIT',
      packages = ["hmako","hmako.ext"],
      zip_safe=False
)
