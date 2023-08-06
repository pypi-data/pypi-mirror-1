# -*- coding: UTF-8 -*-

import os
# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

def setup_module():
    from distutils.core import setup
    import yagt

    setup(
        name='yagt',
        version=yagt.__version__,
        author='Yung-Yu Chen',
        author_email='yungyuc+yagt@gmail.com',
        url='http://bitbucket.org/yungyuc/yagt/',
        description=yagt.__description__.strip(),
        long_description=yagt.__doc__,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'License :: OSI Approved :: BSD License',
            'Topic :: Internet :: WWW/HTTP',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows',
            'Programming Language :: Python',
        ],
        platforms=[
            'Linux',
            'Windows',
        ],
        license='BSD',
        py_modules=[
            'yagt',
        ],
    )

if __name__ == '__main__':
    setup_module()
