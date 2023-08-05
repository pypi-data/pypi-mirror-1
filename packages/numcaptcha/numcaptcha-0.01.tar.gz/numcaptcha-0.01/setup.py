from distutils.core import setup
import ez_setup
ez_setup.use_setuptools()

setup(
    name='numcaptcha',
    version='0.01',
    description='simple number captcha',
    maintainer='Supreet Sethi',
    maintainer_email='supreet.sethi@gmail.com',
    url='http://supreetsethi.net/drupal/',
    py_modules = [ 'numcaptcha'],
    classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    zip_safe=True
    )
