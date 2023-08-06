# Export UPA MemberInfo data as CSV
# 
# Using semicolon as delimiter. Export encoding is 
# iso-8859-15

import csv
from cStringIO import StringIO
from Products.CMFCore.permissions import ManageUsers
from AccessControl import Unauthorized

member = context.portal_membership.getAuthenticatedMember()
portal = context.portal_url.getPortalObject()
if not member.checkPermission(ManageUsers, portal):
    raise Unauthorized('You are not allowed to access the UPA member export ')

brains = context.portal_catalog(portal_type='MemberInfo')
one = brains[0].getObject()
schema = one.Schema()

map = list()

for field in schema.fields():
    if not field.schemata in ('default', 'Membership'):
        continue
    name = field.getName()
    if name in ('id', 'title', 'description'):
        continue
    map.append((field.getName(), field.accessor))


class UPACSV(csv.excel):
    delimiter = ';'
    lineterminator = '\n'
    quoting = csv.QUOTE_ALL


def _c(s, encoding='iso-8859-15'):
    if isinstance(s, int):
        s = str(s)
    if isinstance(s, unicode):
        return s.encode(encoding, 'replace')
    elif isinstance(s, str):
        return unicode(s, 'utf-8').encode(encoding, 'replace')
    else:
        return repr(s)

IO = StringIO()
writer = csv.writer(IO, dialect=UPACSV())

# write first line
writer.writerow([name for name, accessor in map])

objs = [b.getObject() for b in brains]
objs.sort(lambda x,y: cmp(x.getUpaId(), y.getUpaId()))

for mi in objs:
    lst = list()
    for name, accessor in map:
        v = getattr(mi, accessor)()
        lst.append(_c(v))
    writer.writerow(lst)

csv = IO.getvalue()

R = context.REQUEST.RESPONSE
R.setHeader('content-type', 'text/csv')
R.setHeader('content-length', len(csv))
R.setHeader('content-disposition', 'attachment; filename="upa-memberinfo.csv"')
return (csv)

