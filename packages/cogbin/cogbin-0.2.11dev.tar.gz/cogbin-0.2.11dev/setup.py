try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='cogbin',
    version='0.2.11',
    description='Cogbin is a webtool that sync with pypi, it retrives metadata from it and displays the categories you set up in its web interface. It is running for turbogears2 with turbogears2 categories by default but these can be adjusted at any time. Install it, modify the categories, deploy and you have a list of packages for your software community.',
    author='Lukasz Szybalski',
    author_email='szybalski@gmail.com',
    url='https://launchpad.net/cogbin/+download',
    install_requires=[
        "TurboGears2",
        "ToscaWidgets >= 0.9.1",
        "zope.sqlalchemy",
        "repoze.what-quickstart",
        "tgrum",
        #"modwsgideploy",
                ],
    setup_requires=["PasteScript>=1.6.3"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'cogbin': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    keywords = [
        'turbogears2.application'
    ],
    message_extractors = {'cogbin': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = cogbin.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
