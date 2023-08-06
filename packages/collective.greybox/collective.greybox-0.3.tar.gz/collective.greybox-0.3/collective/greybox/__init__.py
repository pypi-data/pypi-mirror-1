
# register skins directory
from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory('skins', globals())

#make it available in quickinstaller
def initialize(context):
    pass
