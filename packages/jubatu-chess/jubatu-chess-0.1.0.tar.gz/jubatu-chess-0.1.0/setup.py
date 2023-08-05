#!/usr/bin/env python
 
from distutils.core import setup
 
setup(name='jubatu-chess',
    version='0.1.0',
    license='X11/MIT with exemptions',
    maintainer='Andreas Naive',
    maintainer_email='andreasnaive@gmail.com',
    url='http://andreasnaive.blogspot.com/',
    description='Jubatu chess plugin',
    long_description='Plugin for the Jubatu package that allow to play chess matchs with other human players through\
the XMPP messaging protocol. It implements a 3d interface.',
    keywords=['games', 'board games', 'chess'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Games/Entertainment :: Turn Based Strategy'
    ],
    requires=['jubatu'],
    packages=['jubatu/games/chess', 'jubatu/games/chess/backend', 'jubatu/games/chess/frontend'],
    package_data={'jubatu/games/chess': ['default.cfg', 'frontend/models/*.egg', 'frontend/textures/*.jpg', 'frontend/i18n/*/*/*.mo', 'i18n/*/*/*.mo']},
)

