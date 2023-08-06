from setuptools import setup, find_packages

setup(
    name = "django-live",
    version = "0.1.7",
    packages = find_packages(),
    author = "nicoechaniz",
    author_email = "nico@rakar.com",
    description = "Comet based chat for django. Similar to humanclick / livephp. Also public rooms",
    url = "http://bitbucket.org/nicoechaniz/django-live/",
    include_package_data = True,

#    package_dir = {'':'live'}
#    package_data = {'live': ['*.txt'],
#                    'live': ['templates/live/*.html']},
    zip_safe = False,
    setup_requires=["setuptools_hg"],
)
