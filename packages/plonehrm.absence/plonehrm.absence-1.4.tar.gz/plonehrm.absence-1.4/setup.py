from setuptools import setup, find_packages
import os

version = '1.4'

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
          'Products.plonehrm>=2.7',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
