

def gensite(self):

    sites = self.objectIds('Plone Site')
    id = 'ub-%d' % (len(sites) + 1)
    factory = self.manage_addProduct['CMFPlone']
    factory.addPloneSite(id, create_userfolder=True, extension_ids=('Products.ubCore:ubCore.default',))
    plone = self[id]
#    plone.setupMembers()
    self.REQUEST.RESPONSE.redirect(plone.absolute_url())
