from setuptools import setup

setup(
    name='django-standalone',
    version='0.3',
    description='use the Django ORM with standalone scripts',
    author='Georg Bauer',
    author_email='gb@rfc1437.de',
    url='http://bitbucket.org/rfc1437/django-standalone/',
    packages=['standalone'],
    scripts=['example_script.py', 'test.py'],
    long_description = file('README').read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    keywords = "django standalone script orm",
    license = 'BSD',
    install_requires = ['django'],
)
