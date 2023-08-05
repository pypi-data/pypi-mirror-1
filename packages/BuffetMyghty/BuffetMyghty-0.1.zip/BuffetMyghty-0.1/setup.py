from setuptools import setup, find_packages

setup(
    name="BuffetMyghty",
    version="0.1",
    description="Myghty templating language plugin",
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
    
