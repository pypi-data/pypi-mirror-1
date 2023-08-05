"""
 genere par la commande "paster restcontroller admin_user admin.auth_user"

"""


import logging

from authproxy.lib.base import *

log = logging.getLogger("authproxy" )


def parse_query_string(content):
    """
        parse a string like that into
        username=me&password=me&group=guest&roles=admin&roles=reviewer
    ((username,me),(group,guest),(roles,admin)(roles,reviewer)
    
    """
    result=[]
    entries=content.split('&')
    for e in entries:
        k,v=e.split("=")
        result.append([k,v])
    return result


class AuthUserController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('admin', 'auth_user', controller='admin/auth_user', 
    #         path_prefix='/admin', name_prefix='admin_')


    def index(self, format='html'):
        """GET /admin_auth_user: All items in the collection."""
        # url_for('admin_auth_user')
        return "admin auth user Page"
        pass

    def create(self):
        """POST /admin_auth_user: Create a new item."""
        # url_for('admin_auth_user')
        log.debug("create a user")
        #elements=parse_query_string(request.environ["QUERY_STRING"])
        #log.debug("query_string:%s" % str(elements))
                                                    
        return self.show('new_user')
        #h.redirect('show/newone')
        

    def new(self, format='html'):
        """GET /admin_auth_user/new: Form to create a new item."""
        # url_for('admin_new_admin_user')
        log.debug("form for a new user")
        c.users=request.environ['authkit.users']
        return render('genshi','user')


    def update(self, id):
        """PUT /admin_auth_user/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('admin_admin_user', id=ID),
        #           method='put')
        # url_for('admin_admin_user', id=ID)
        pass

    def delete(self, id):
        """DELETE /admin_auth_user/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('admin_admin_user', id=ID),
        #           method='delete')
        # url_for('admin_admin_user', id=ID)
        pass

    def show(self, id, format='html'):
        """GET /admin_auth_user/id: Show a specific item."""
        # url_for('admin_admin_user', id=ID)
        log.debug("show user id:%s" % id )
        return "auth user show %s" %id
        pass

    def edit(self, id, format='html'):
        """GET /admin_auth_user/id;edit: Form to edit an existing item."""
        # url_for('admin_edit_admin_user', id=ID)
        pass
