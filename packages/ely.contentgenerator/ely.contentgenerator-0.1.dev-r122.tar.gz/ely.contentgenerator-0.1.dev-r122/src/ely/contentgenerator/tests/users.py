from Products.CMFCore.utils import getToolByName

USERS = {
         'admin':{'passw': 'password', 'roles': ['Manager']},
         'member_1':{'passw': 'password', 'roles': ['Member']},
         'member_2':{'passw': 'password', 'roles': ['Member']},
         'reviewer_1':{'passw': 'password', 'roles': ['Reviewer']},
        }

def setupUsers(test_context):
    """
    Set up some users to test with
    """
    test_context.loginAsPortalOwner()

    test_context.membership = getToolByName(test_context.portal,
                                            'portal_membership', None)
    for user_id in USERS.keys():
        test_context.membership.addMember(user_id,
                                          USERS[user_id]['passw'],
                                          USERS[user_id]['roles'], [])
