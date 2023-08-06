import sys
from setuptools import setup, find_packages

# hack around different dependencies for different python versions
deps = ['docutils>=0.3']
if sys.version_info < (2, 6):
    deps.insert(0, 'ssl')

setup(
    name = "HypnoAPNSWrapper",
    version = "0.3-7",
    packages = find_packages('.'),
    classifiers = ["Intended Audience :: Customer Service", "Topic :: Internet" ],
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = deps,

    package_data = {
        '': ['*.dat'],
    },

    # metadata for upload to PyPI
    author = "Max Klymyshyn, Sonettic, Jan Huelsbergen",
    author_email = "klymyshyn@gmail.com",
    description = "This is wrapper for Apple Push Notification Service.",
    license = "ALv2",
    keywords = "apns push notification service wrapper apple",
    url = "http://code.google.com/p/apns-python-wrapper/",
	long_description = """
		The Wrapper support for Alerts, Badges, Sounds and Custom arguments.		
		Feedback Service wrapper support for iterations through feedback tuples.

        This version has been modified to be easily installable with python 2.6.
	
	"""
)
