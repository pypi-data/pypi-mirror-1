from setuptools import setup, find_packages
import os

version = '1.0b5'

history_path = os.path.join('plonehrm', 'absence', 'HISTORY.txt')
history_file = open(history_path)
history = history_file.read().strip()
history_file.close()



setup(name='plonehrm.absence',
      version=version,
      description="Register employee absence",
      long_description=history,
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url="",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonehrm'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
