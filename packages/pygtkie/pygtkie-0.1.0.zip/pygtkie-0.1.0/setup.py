from distutils.core import setup

setup(
      name =                'pygtkie', 
      version =             '0.1.0',
      description =         'Python GTK Internet Explorer Component',
      author =              'Vaclav Opekar, Eccam, s.r.o.',
      author_email =        'opekar@eccam.com',
      url =                 'www.eccam.com',
      packages =            ['pygtkie', 'pygtkie/generated'],
      requires =    ['pywin32', 'pygtk']
      )