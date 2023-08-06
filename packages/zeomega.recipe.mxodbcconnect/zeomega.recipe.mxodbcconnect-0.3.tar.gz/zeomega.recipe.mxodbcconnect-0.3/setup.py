from setuptools import setup, find_packages

setup(name='zeomega.recipe.mxodbcconnect',
      version='0.3',
      description="A buildout recipe to install eGenix mx.ODBCConnect.Client",
      long_description="""\
A buildout recipe to install eGenix mx.ODBCConnect.Client""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "Framework :: Buildout",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Buildout recipe mx.ODBCConnect.Client',
      author='Senthil',
      author_email='orsenthil@gmail.com',
      url='http://www.zeomega.com',
      license='GPL',
      packages=find_packages('src'),
      package_dir={"": "src"},
      namespace_packages=['zeomega', 'zeomega.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'setuptools',
        ],
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = zeomega.recipe.mxodbcconnect:Recipe
      """,
      )
