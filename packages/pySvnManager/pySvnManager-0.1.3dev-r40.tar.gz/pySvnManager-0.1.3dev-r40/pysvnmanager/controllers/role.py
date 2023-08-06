# -*- coding: utf-8 -*-
import logging

from pysvnmanager.lib.base import *
from pysvnmanager.model.svnauthz import *

log = logging.getLogger(__name__)

class RoleController(BaseController):
    requires_auth = True

    def __init__(self):
        self.authz = SvnAuthz(cfg.authz_file)
        self.login_as = session.get('user')
        # Used as checked in user to rcs file.
        self.authz.login_as = self.login_as
        self.aliaslist  = map(lambda x:x.uname, self.authz.aliaslist)
        self.userlist = map(lambda x:x.uname, self.authz.userlist)
        self.grouplist = map(lambda x:x.uname, self.authz.grouplist)

    def __before__(self, action):
        super(RoleController, self).__before__(action)
        if not self.authz.is_super_user(self.login_as):
            return redirect_to(h.url_for(controller='security', action='failed'))

    def index(self):
        c.revision = self.authz.version
        c.aliaslist  = self.aliaslist
        c.userlist = self.userlist
        c.grouplist = self.grouplist
        return render('/role/index.mako')
    
    def get_role_info(self, role=None):
        members_count = 0;
        msg = ''
        if not role:
            d = request.params
            role = d.get('role')

        # get javascript code for top_form's role_selector
        if not role:
            msg += 'id[0]="%s";' % '...'
            msg += 'name[0]="%s";\n' % _("Please choose...")
            members_count += 1;
            for uname in self.grouplist:
                if uname == '*' or uname[0] == '$':
                    continue
                msg += 'id[%d]="%s";' % (members_count, uname)
                assert uname[0] == '@'
                msg += 'name[%d]="%s";\n' % (members_count, _("Group:")+uname[1:])
                members_count += 1;
            for uname in self.aliaslist:
                msg += 'id[%d]="%s";' % (members_count, uname)
                assert uname[0] == '&'
                msg += 'name[%d]="%s";\n' % (members_count, _("Alias:")+uname[1:])
                members_count += 1;
            msg += 'members_count=%d;\n' % members_count

        else:
            roleobj = self.authz.get_userobj(role)

            # get javascript code for g_form's group_member_list
            if roleobj and role[0] == '@':
                for i in roleobj:
                    uname = i.uname
                    #if uname == '*' or uname[0] == '$':
                    #    continue
                    msg += 'id[%d]="%s";' % (members_count, uname)
                    if uname[0] == '@':
                        msg += 'name[%d]="%s";\n' % (members_count, _("Group:")+uname[1:])
                    elif uname[0] == '&':
                        msg += 'name[%d]="%s";\n' % (members_count, _("Alias:")+uname[1:])
                    else:
                        msg += 'name[%d]="%s";\n' % (members_count, uname)
                    members_count += 1;
                msg += 'members_count=%d;\n' % members_count

            # get javascript code for a_form's alias as username
            elif roleobj and role[0] == '&':
                msg +='aliasname = "%s";' % roleobj.uname
                msg +='username = "%s";\n' % roleobj.username
        
        msg += 'revision="%s";\n' % self.authz.version
        return msg
        
    def save_group(self):
        d = request.params
        member_list = []
        msg = ""

        rolename = d.get('rolename')
        autodrop = d.get('autodrop', 'no')
        members  = d.get('members', '')
        revision  = d.get('revision', self.authz.version)

        if autodrop.lower()=='yes':
            autodrop = True
        else:
            autodrop = False

        member_list.extend(map(lambda x: x.strip(), members.split(',')))
        
        log_message = _(u"User %(user)s changed group: %(grp)s. (rev:%(rev)s)") % \
                         {'user':session.get('user'), 'grp': rolename, 'rev': revision}

        try:
            self.authz.set_group(rolename, member_list, autodrop=autodrop)
            self.authz.save(revision, comment=log_message)
        except Exception, e:
            msg = get_unicode(e[0])

        log.info(log_message)
        if msg: log.error(msg)
        
        return msg
    
    def delete_group(self):
        d = request.params
        rolename = d.get('role')
        revision  = d.get('revision', self.authz.version)
        msg = ''
        
        log_message = _(u"User %(user)s delete group: %(grp)s. (rev:%(rev)s)") % \
                         {'user':session.get('user'), 'grp': rolename, 'rev': revision}

        if rolename:
            try:
                self.authz.del_group(rolename)
                self.authz.save(revision, comment=log_message)
            except Exception, e:
                msg = get_unicode(e[0])

        log.info(log_message)
        if msg: log.error(msg)

        return msg
        
    def save_alias(self):
        d = request.params
        aliasname = d.get('aliasname')
        username = d.get('username')
        revision  = d.get('revision', self.authz.version)
        msg = ""
        
        log_message = _(u"User %(user)s changed alias: %(alias)s. (rev:%(rev)s)") % \
                     {'user':session.get('user'), 'alias': aliasname, 'rev': revision}

        try:
            self.authz.add_alias(aliasname, username)
            self.authz.save(revision, comment=log_message)
        except Exception, e:
            msg = get_unicode(e[0])

        log.info(log_message)
        if msg: log.error(msg)
        
        return msg
    
    def delete_alias(self):
        d = request.params
        aliasname = d.get('aliasname')
        revision  = d.get('revision', self.authz.version)
        msg = ''
        
        log_message = _(u"User %(user)s delete alias: %(alias)s. (rev:%(rev)s,%(msg)s)") % \
                 {'user':session.get('user'), 'alias': aliasname, 'rev': revision, 'msg': msg}

        if aliasname:
            try:
                self.authz.del_alias(aliasname)
                self.authz.save(revision, comment=log_message)
            except Exception, e:
                msg = get_unicode(e[0])

        log.info(log_message)
        if msg: log.error(msg)

        return msg

        
