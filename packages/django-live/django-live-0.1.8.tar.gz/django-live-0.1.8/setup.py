from setuptools import setup, find_packages
import live

setup(
    name = "django-live",
    version = live.__version__,
    packages = find_packages(),
    author = "nicoechaniz",
    author_email = "nico@rakar.com",
    description = "Comet based chat for django. Similar to humanclick / livephp. Also public rooms",
    url = "http://bitbucket.org/nicoechaniz/django-live/",
    include_package_data = True,
    zip_safe = False,
#    setup_requires=["setuptools_hg"],
)
