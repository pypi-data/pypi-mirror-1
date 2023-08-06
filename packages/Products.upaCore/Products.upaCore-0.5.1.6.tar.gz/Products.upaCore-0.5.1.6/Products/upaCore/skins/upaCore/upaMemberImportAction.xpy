##parameters=csvfile=''

from AccessControl import Unauthorized
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.permissions import ManageUsers
import csv
import pprint
import cStringIO

pr = context.portal_registration
pm = context.portal_membership
wf = context.portal_workflow
portal = context.portal_url.getPortalObject()


class UPACSV(csv.excel):
    delimiter = ';'
    lineterminator = '\n'
    quoting = csv.QUOTE_ALL

member = pm.getAuthenticatedMember()
if not member.checkPermission(ManageUsers, portal):
    raise Unauthorized('You are not allowed to access the UPA member import')

def _c(s):
    return unicode(s, 'utf-8').encode('iso-8859-15')

def newUsername(firstname, lastname):
    s = '%s%s' % (firstname, lastname)
    s = s.lower()
    s = s.replace(' ', '')
    s = s.replace('_', '')
    s = s.replace('-', '')
    s = s.replace('.', '')
    s = s.replace('ä', 'ae')
    s = s.replace('ü', 'ue')
    s = s.replace('ö', 'oe')
    s = s.replace('ß', 'ss')
    return s

map = dict()
reader = csv.reader(csvfile, dialect=UPACSV())
for i, line in enumerate(reader):
    if not line:
        continue

    if i==0:
        for j, key in enumerate(line):
            map[j] = key.strip()        
        continue

    d = dict()
    for j, value in enumerate(line):
        d[map[j]] = value

    print '-'*80
    IO = cStringIO.StringIO()
    pprint.pprint(d, stream=IO)
    print IO.getvalue()

    try:
        upa_id = int(d['member_id'])
    except:
        upa_id = 0

    salutation = dict(Herr='Mr.', Frau='Mrs.').get(d['salutation'], '')
    title =  d['title']
    firstname = d['name']
    lastname = d['Nachname']
    email_company = d['email_organization']
    email_private = d['email_private']
    organization = d['organization']
    associated_member = d['associate_member']
    entry_date = d['entry-date']
    account_active = 'y' in d['active_account (y/n)']
    newsletter_abo = 'y' in d['newsletter_abo (y/n)']
    address1 = d['adress1']
    address2 = d['adress2']
    zip = d['zipcode']
    city = d['city']
    country = d['country']
    icom_abo = 'y' in d['icom_abo (y/n)']
    if country == 'D':
        country = 'Germany'
    elif country == 'CH':
        country = 'Swiss'
    elif country == 'A':
        country = 'Austria'

    username = newUsername(_c(firstname), _c(lastname))
    password = pr.generatePassword()
    properties = dict(email=email_company, 
                      fullname='%s %s' % (firstname, lastname))

    print username
    try:
        pr.addMember(username, 
                     password, 
                     roles=('Member',)) 
    except:
        print ' -> Name already taken:' , username
        continue

    member = pm.getMemberById(username)
    member.setMemberProperties(properties)
    pm.createMemberArea(username)
    member_folder = portal.Members[username]

    member_folder.invokeFactory('MemberInfo', 
                                id='index_html',
                                firstName=firstname,
                                salutation=salutation,
                                academicTitle=title,
                                lastName=lastname,
                                address1=address1,
                                address2=address2,
                                zipCode=zip,
                                city=city,
                                country=country,
                                organization=organization,
                                emailPrivate=email_private,
                                emailCompany=email_company,
                                membershipLevel=d['member_typ'],
                                associatedMembership=associated_member,
                                newsletterSubscription=newsletter_abo,
                                entryDate=entry_date,
                                accountActive=account_active,
                                icomSubscription=icom_abo,
                                phone=d['phone'],
                                fax=d['fax'],
                                mobile=d['mobile'],
                                upaId=upa_id,
                               )

    member_info = member_folder.index_html
    context.plone_utils.changeOwnershipOf(member_folder, username, recursive=True)
    wf.doActionFor(member_folder, 'publish')
    wf.doActionFor(member_info, 'publish')
    print '  ->  OK'

return printed
