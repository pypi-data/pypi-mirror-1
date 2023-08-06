from setuptools import setup, find_packages
 
setup(
    name='django-readonlywidget',
    version='0.2',
    description='A ReadOnly Widget for Django',
    author='Stephan Jaekel',
    author_email='steph@rdev.info',
    url='http://bitbucket.org/stephrdev/django-readonlywidget/src/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
)
