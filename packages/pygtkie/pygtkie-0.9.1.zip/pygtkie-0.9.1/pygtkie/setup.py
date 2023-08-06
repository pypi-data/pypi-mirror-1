from distutils.core import setup

setup(
      name =                'pygtkie', 
      version =             '0.9.1',
      description =         'Python GTK Internet Explorer Component',
      author =              'Vaclav Opekar, Eccam, s.r.o.',
      author_email =        'opekar@eccam.com',
      url =                 'www.eccam.com',
      packages =            ['pygtkie', 'pygtkie/generated'],
      install_requires =    ['pywin32']
      )