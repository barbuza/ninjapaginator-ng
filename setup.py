from setuptools import setup, find_packages
setup(
    name = "django-ninjapaginator-ng",
    version = "0.1.6",
    packages = find_packages(),
    author = "Anderson",
    author_email = "self.anderson@gmail.com",
    description = "Django application with multiple type of pagination integrated",
    license = "BSD",
    keywords = "django",
    url = "https://github.com/barbuza/ninjapaginator-ng",
    install_requires = ["django-annoying"],
    include_package_data = True,
    zip_safe = False
)

