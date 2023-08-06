##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

""" Add a Zope management user to the root Zope user folder """

import sys
from repoze.zope2.scripts.finder import ZopeFinder

def adduser(app, user, pwd):
    import transaction
    result = app.acl_users._doAddUser(user, pwd, ['Manager'], [])
    transaction.commit()
    return result

def main(argv=sys.argv):
    import sys
    try:
        user, pwd = argv[1], argv[2]
    except IndexError:
        print "%s <username> <password>" % argv[0]
        sys.exit(255)
    finder = ZopeFinder(argv)
    finder.filter_warnings()
    app = finder.get_app()
    adduser(app, user, pwd)

if __name__ == '__main__':
    main()
    
