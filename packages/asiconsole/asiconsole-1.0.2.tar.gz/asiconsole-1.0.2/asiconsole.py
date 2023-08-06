#! /usr/bin/env python
#
# Copyright (c) 2009, Nokia Corp.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Nokia nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED THE COPYRIGHT HOLDERS AND CONTRIBUTORS ''AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import with_statement # for Python 2.5

__author__ = 'eemeli.kantola@iki.fi (Eemeli Kantola)'

def find_friends(query):
    users = conn.find_users(query)
    if len(users) == 0:
        print('No matching users')
        return
    
    user = users[0]
    print('First matching user: %s' % user['username'])
    friends = conn.get_friends(user['id'])
    print('Friends of %s: %s' % (user['username'], map(lambda x: x['username'], friends)))

def main():
    import asilib

    # Debug messages on
    asilib.debug = True

    banner = '''
    ASI console, connected to %s as %s
    Useful variables:
    
        ac:   ASIConnection with an application session open
        aid:  application id = %s
        
        uc:   ASIConnection with a user session open
        uid:  user id = %s
'''

    import os
    conf = {}
    execfile(os.getenv('HOME', '.') + '/.asirc', conf)
    if not ('asi_app_params' in conf and 'asi_user_params' in conf):
        print('asi_app_params or asi_user_params not defined.')
        sys.exit(1)
    
    with asilib.ASIConnection(**conf['asi_app_params']) as ac:
        print('ac.session = %s' % ac.session)
        aid = ac.session['entry']['app_id']
        
        with asilib.ASIConnection(**conf['asi_user_params']) as uc:
            print('uc.session = %s' % uc.session)
            uid = uc.session['entry']['user_id']
            
            banner = banner % (conf['asi_app_params']['base_url'], conf['asi_app_params']['app_name'], aid, uid)
            
            import IPython
            IPython.Shell.IPShell(user_ns=locals()).mainloop(sys_exit=1, banner=banner)

if __name__ == '__main__':
    main()
