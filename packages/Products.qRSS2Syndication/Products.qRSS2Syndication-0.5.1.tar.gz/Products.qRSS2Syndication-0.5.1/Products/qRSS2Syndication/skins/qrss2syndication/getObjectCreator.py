## Script (Python) "getMemberEmail"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=MemberId
##title=
##
memberlist = context.portal_membership.searchForMembers(REQUEST=None, name=MemberId)
res = None
if memberlist:
    for member in memberlist:
        if member.id == MemberId:
            res = member
            break
return res