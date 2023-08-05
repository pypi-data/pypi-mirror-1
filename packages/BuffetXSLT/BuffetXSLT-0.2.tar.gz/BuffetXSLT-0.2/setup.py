from setuptools import setup, find_packages

setup(
    name="BuffetXSLT",
    version="0.2",
    license="MIT",
    description="XSLT templating plugin",
    long_description="""\
Uses Amara for XSLT templating.
This plugin is compatible with the Buffet templating filter for CherryPy
and with the TurboGears megaframework.
    """,
    author="Sylvain Hellegouarch, Christian Wyglendowski",
    author_email="christian@dowski.com",
    url="http://projects.dowski.com/projects/buffetxslt",
    #scripts = [],
    packages=find_packages(),
    zip_safe=False,
    entry_points = """
        [python.templating.engines]
        xslt = buffetxslt.xsltsupport:BuffetXSLTPlugin
        """
    )
    
