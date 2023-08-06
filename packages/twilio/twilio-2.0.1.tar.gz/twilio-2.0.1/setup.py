from distutils.core import setup
setup(
    name = "twilio",
    py_modules = ['twilio'],
    version = "2.0.1",
    description = "Twilio API client and TwiML generator",
    author = "Twilio",
    author_email = "help@twilio.com",
    url = "http://github.com/twilio/twilio-python/",
    download_url = "http://github.com/twilio/twilio-python/tarball/2.0.1",
    keywords = ["twilio","twiml"],
    classifiers = [
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Telephony"
        ],
    long_description = """\
    Python Twilio Helper Library
    ----------------------------
    
    DESCRIPTION

    The Twilio REST
    """
)