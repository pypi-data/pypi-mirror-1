from setuptools import setup, find_packages

setup(
    name = "django-dojoserializer",
    version = "1.1.2",
    url = 'http://code.google.com/p/django-dojoserializer',
    license = 'MIT',
    description = "Serializes django model instances to a dojo data " + \
        "compatible JSON representation",
    author = 'Fabian Topfstedt',
    author_email = 'myfirstname@mylastname.de',
    package_data = {
        'src/dojoserializer': [
            'templatetags/*.py',
        ]
    },
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)
