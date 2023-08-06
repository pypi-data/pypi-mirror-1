try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


version = '0.1'
requirements = ['paramiko']


setup(
    name="socksproxy",
    version=version,
    packages=['socksproxy'],
    install_requires=requirements,
    entry_points={'console_scripts': ['socksproxy = socksproxy.main:main']},
    description='SOCKS4/5 proxy with SSH support.',
    author='Dave St.Germain',
    author_email='dave@st.germa.in',
    url='http://bitbucket.org/dcs/socksproxy/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: Proxy Servers',
    ],
)
