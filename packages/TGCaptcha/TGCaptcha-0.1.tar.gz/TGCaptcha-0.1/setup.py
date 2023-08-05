from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("tgcaptcha", "release.py"))

setup(
    name="TGCaptcha",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    #download_url=download_url,
    license=license,
    
    install_requires = ["TurboGears >= 1.0.1",
        "pycrypto >= 2.0.1"],
    # dependency_links = ['http://effbot.org/downloads/'],
    zip_safe=True,
    packages=find_packages(exclude=['tests']),
    package_data = find_package_data(where='tgcaptcha',
                                     package='TGCaptcha'),
    keywords = [
        'turbogears.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Widgets',
    ],
    entry_points = """
        [turbogears.widgets]
            tgcaptcha = tgcaptcha.widgets
        [tgcaptcha.jpeg_generators]
            mcdermott = tgcaptcha.plugins.image.mcdermott:generate_jpeg
            vanasco_dowty = tgcaptcha.plugins.image.vanasco_dowty:generate_jpeg
        [tgcaptcha.text_generators]
            random_ascii = tgcaptcha.plugins.text.random_ascii:generate_text
        [paste.paster_create_template]
            tgcaptcha = tgcaptcha:TGCaptchaConfig
    """,
    test_suite = 'nose.collector',
    )
    
