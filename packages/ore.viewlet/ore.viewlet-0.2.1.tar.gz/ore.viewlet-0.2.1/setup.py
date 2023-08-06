from setuptools import setup, find_packages

setup(
    name="ore.viewlet",
    version="0.2.1",
    install_requires=['setuptools', 'zc.table >= 0.5'],
    dependency_links=['http://download.zope.org/distribution/',],
    packages=find_packages('src', exclude=["*.tests", "*.ftests"]),
    
    package_dir= {'':'src'},
    
    namespace_packages=['ore'],
    package_data = {
    '': ['*.txt', '*.zcml', '*.gif', '*.js', '*.pt'],
    },

    zip_safe=False,
    author='Kapil Thangavelu',
    author_email='info@objectrealms.net',
    description="""\
    These are some extensions of the base zope.viewlet model, preconstructed
    viewlets for container management, and new primitives like a private event
    channel, and private annotation storage on the viewlet manager, multipage/wizard
    viewlets, and formlib viewlets.
    """,
    license='GPL',
    keywords="zope zope3",
    )
