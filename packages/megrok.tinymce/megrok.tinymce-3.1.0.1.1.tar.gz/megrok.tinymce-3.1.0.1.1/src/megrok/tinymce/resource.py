import grok
from megrok import resourcelibrary

class TinyMCE(resourcelibrary.ResourceLibrary):
    grok.name('TinyMCE')
    resourcelibrary.directory('tiny_mce')
