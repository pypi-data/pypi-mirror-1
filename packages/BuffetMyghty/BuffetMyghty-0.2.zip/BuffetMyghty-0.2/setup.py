from setuptools import setup, find_packages

setup(
    name="BuffetMyghty",
    version="0.2",
    license="MIT",
    description="Myghty templating language plugin",
    long_description="""
A templating plugin for using Myghty templates.  Publishes end_point 'myghty'
in 'python.templating.engines'. For details about the plugin interface, see:

http://www.turbogears.org/docs/plugins/template.html""",
    author="Christian Wyglendowski",
    author_email="christian@dowski.com",
    url="http://projects.dowski.com/projects/buffetmyghty",
    #scripts = [],
    packages=find_packages(),
    zip_safe=False,
    entry_points = """
        [python.templating.engines]
        myghty = buffetmyghty.myghtysupport:MyghtyTemplatePlugin
    """
    )
    
