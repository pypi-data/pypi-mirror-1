# Created by Noah Kantrowitz on 2007-05-27.
# Copyright (c) 2007 Noah Kantrowitz. All rights reserved.

try:
    import subprocess
except ImportError:
    import _subprocess as subprocess

from trac.core import *
from trac.config import Option

from acct_mgr.api import IPasswordStore

class PwAuthStore(Component):
    """A password backend for AccountManager that uses pwauth."""
    
    implements(IPasswordStore)
    
    pwauth_path = Option('pwauth', 'path', default='/usr/sbin/pwauth',
                         doc='Path to the pwauth program')
    
    def check_password(self, user, password):
        proc = subprocess.Popen([self.pwauth_path], stdin=subprocess.PIPE)
        proc.communicate('%s\n%s\n'%(user, password))
        return proc.returncode == 0
