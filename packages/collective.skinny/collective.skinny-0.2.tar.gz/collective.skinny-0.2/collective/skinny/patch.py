# We patch a 'standard_error_message' into the Plone site.  This frees
# us from having to register a skins directory to override the normal
# 'standard_error_message':
from Products.CMFPlone.Portal import PloneSite

def patch_standard_error_message():
    def standard_error_message(self, **kwargs):
        return self.restrictedTraverse('@@404.html')()
    PloneSite.standard_error_message = standard_error_message

patch_standard_error_message()
