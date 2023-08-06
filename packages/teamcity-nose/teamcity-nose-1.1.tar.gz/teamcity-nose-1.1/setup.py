from setuptools import setup
setup(
    name = "teamcity-nose",
    version = "1.1",
    author = 'Leonid Shalupov',
    author_email = 'Leonid.Shalupov@jetbrains.com',
    description = 'A nose plugin to send test result messages '+
        'to TeamCity continuous integration server',
    long_description = """Just install this python egg to
enable reporting test results to TeamCity server.

Plugin will activate itself only under TeamCity build
(which is detected by presence of environment variable
TEAMCITY_PROJECT_NAME)
""",
    license = 'Apache 2.0',
    keywords = 'unittest nose teamcity test',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing'
        ],
    url = "http://pypi.python.org/pypi/teamcity-nose",
    platforms = ["any"],

    install_requires = [
        "nose >=0.10,<0.11",
        "teamcity-messages >=1.0"
    ],

    entry_points = {
        'nose.plugins.0.10': [
            'nose-teamcity = teamcity.nose_report:TeamcityReport'
        ]
    },
)
