import ez_setup

ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django-live",
    version = "0.1.1",
    packages = find_packages(),
    author = "NicoEchaniz",
    author_email = "nico@rakar.com",
    description = "Comet based chat for django. Similar to humanclick / livephp. Also public rooms",
    url = "http://nicoechaniz.com.ar",
    include_package_data = True
)
