"""
 genere par la commande 'paster restcontroller admin admin.auth_permission'
"""
import logging

from authproxy.lib.base import *

log = logging.getLogger(__name__)

class AuthPermissionController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py file has
    # a resource setup:
    #     map.resource('admin', 'auth_permission', controller='admin/auth_permission', 
    #         path_prefix='/admin', name_prefix='admin_')


    def index(self, format='html'):
        """GET /admin_auth_permission: All items in the collection."""
        # url_for('admin_auth_permission')
        pass

    def create(self):
        """POST /admin_auth_permission: Create a new item."""
        # url_for('admin_auth_permission')
        pass

    def new(self, format='html'):
        """GET /admin_auth_permission/new: Form to create a new item."""
        # url_for('admin_new_admin')
        pass

    def update(self, id):
        """PUT /admin_auth_permission/id: Update an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(h.url_for('admin_admin', id=ID),
        #           method='put')
        # url_for('admin_admin', id=ID)
        pass

    def delete(self, id):
        """DELETE /admin_auth_permission/id: Delete an existing item."""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(h.url_for('admin_admin', id=ID),
        #           method='delete')
        # url_for('admin_admin', id=ID)
        pass

    def show(self, id, format='html'):
        """GET /admin_auth_permission/id: Show a specific item."""
        # url_for('admin_admin', id=ID)
        pass

    def edit(self, id, format='html'):
        """GET /admin_auth_permission/id;edit: Form to edit an existing item."""
        # url_for('admin_edit_admin', id=ID)
        pass
