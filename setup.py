from setuptools import setup, find_packages
setup(
    name = "django-ninjapaginator",
    version = "0.1.2",
    packages = find_packages(),
    author = "Anderson",
    author_email = "self.anderson@gmail.com",
    description = "Django application with multiple type of pagination integrated",
    license = "BSD",
    keywords = "django",
    url = "http://www.assembla.com/wiki/show/ninja-paginator",
    install_requires = ["django-annoying"],
    include_package_data = True,
    zip_safe = False
)

