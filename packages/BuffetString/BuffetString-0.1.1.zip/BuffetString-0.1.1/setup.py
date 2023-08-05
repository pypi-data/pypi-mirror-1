from setuptools import setup, find_packages

setup(
    name="BuffetString",
    version="0.1.1",
    description="Python string Template plugin",
    author="Christian Wyglendowski",
    author_email="christian@dowski.com",
    url="http://projects.dowski.com/projects/buffetstring",
    #scripts = [],
    packages=find_packages(),
    zip_safe=False,
    entry_points = """
        [python.templating.engines]
        string = buffetstring.stringsupport:StringTemplatePlugin
    """
    )
    
