from distutils.core import setup
setup(name='lazy_paginator',
      version='0.1',
      description='Lazy Paginator for Django',
      author="Andy McKay",
      author_email="andy@clearwind.ca",
      packages=["lazy_paginator",],
      package_dir = {'lazy_paginator':'src'},
      classifiers = [
        "Development Status :: 4 - Beta",
        "Framework :: Django"
        ]
      )