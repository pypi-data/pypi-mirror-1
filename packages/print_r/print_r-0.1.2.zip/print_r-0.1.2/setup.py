from setuptools import setup, find_packages
setup(name='print_r',
      py_modules=["print_r", "tests"],
      version='0.1.2',
      description=("php print_r for python"),
      classifiers=[
        "Programming Language :: Python",
        ("Topic :: Software Development :: Libraries :: Python Modules"),
        ],
      keywords='php print_r',
      author='Marc Belmont',
      author_email='code-marcbelmont-com',
      url="http://wiki.github.com/marcbelmont/python-print_r",
      packages=find_packages(),
      )
