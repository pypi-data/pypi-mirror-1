import grok
from megrok import resourcelibrary

class YUI(resourcelibrary.ResourceLibrary):
    grok.name('YUI')
    resourcelibrary.directory('yui-build')

