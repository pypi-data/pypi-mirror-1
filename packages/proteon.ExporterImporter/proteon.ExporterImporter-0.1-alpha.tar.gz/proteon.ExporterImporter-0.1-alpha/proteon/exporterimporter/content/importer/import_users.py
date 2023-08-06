from Products.CMFCore.utils import getToolByName
from cStringIO import StringIO
from csv import reader, writer

def run(self):
    portal = self
    pmemb = getToolByName(portal,'portal_membership')

    response = portal.REQUEST.response

    response.setHeader('content-type', 'text/csv')
    response.setHeader('content-disposition',
                       'inline; filename=knmp_members.csv');

    pseudoFile = StringIO()
    w = writer(pseudoFile)

    w.writerow(['username','password','email','roles'])
    for memb in pmemb.listMembers():
        w.writerow([memb.id,
                    memb.getPassword(),
                    memb.getEmail(),
                    memb.getRoles(),])
                    #tuple(memb.getGroups())])

    pseudoFile.seek(0)
    csv = pseudoFile.read()
    pseudoFile.close()

    return csv
