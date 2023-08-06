from Products.Archetypes.ReferenceEngine import Reference
from Products.Archetypes.exceptions import ReferenceException

class BidirectionalReference(Reference):

    def addHook(self, tool, sobj=None, tobj=None):
        if not (tobj.hasRelationshipTo(sobj, self.relationship) or \
                hasattr(tobj, '_v_addingReference')):
            sobj._v_addingReference = 1
            tool.addReference(tobj, sobj, self.relationship,
                referenceClass=BidirectionalReference)
            del sobj._v_addingReference

    def delHook(self, tool, sobj=None, tobj=None):
        if tobj.hasRelationshipTo(sobj, self.relationship) and \
           not hasattr(tobj, '_v_deletingReference'):
            sobj._v_deletingReference = 1
            tool.deleteReference(tobj, sobj.UID(), self.relationship)
            del sobj._v_deletingReference

SymmetricalReference = BidirectionalReference
