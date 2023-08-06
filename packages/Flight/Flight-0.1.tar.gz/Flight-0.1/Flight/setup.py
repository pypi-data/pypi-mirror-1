from setuptools import setup, find_packages
setup(
      name = "Flight",
      version = "0.1",
      packages = find_packages(),
      author = "William Coleman",
      author_email = "weecol@unlimitedmail.org",
      install_requires = ['setuptools'],
      package_data = {
            'Flight': ['*.py'],          
      },
      license = "PSF",
      entry_points = {
                      'gui_scripts': [
                                      'Flight_pilot = Flight.pilot',
                                      ],
                      },
)