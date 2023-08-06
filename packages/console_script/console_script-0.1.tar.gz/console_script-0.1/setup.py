from setuptools import find_packages, setup

version='0.1'

setup(name='console_script',
      version=version,
      description="pastescript template for creating command line applications",
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org',
      keywords='trac plugin',
      license="",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests*']),
      include_package_data=True,
      install_requires = [ 'PasteScript' ],
      zip_safe=False,
      entry_points = """
      [paste.paster_create_template]
      console_script = console_script:console_script
      """,
      )

