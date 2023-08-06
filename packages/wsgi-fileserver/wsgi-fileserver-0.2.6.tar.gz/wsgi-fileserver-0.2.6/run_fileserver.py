#!/usr/bin/env python
#   Copyright (c) 2006-2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# -- Example server run

if __name__ == "__main__":
    import sys
    from wsgiref import simple_server
    import logging
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    if len(sys.argv) is 1:
        print 'Usage: python run_fileserver path=/usr/local/files host=127.0.0.1 port=8080 mountpoint=/files'
        sys.exit
    
    args = {'port':8080, 'host':'127.0.0.1', 'mountpoint':None}
    sys.argv.pop(0)
    for arg in sys.argv:
        if arg.find('=') is -1:
            print 'args must be in key=value format'
            sys.exit()
        args.__setitem__(*arg.split('='))
        
    assert args.has_key('path')
    
    import wsgi_fileserver
    application = wsgi_fileserver.WSGIFileServerApplication(root_path=args['path'], mount_point=args['mountpoint'])
    
    server = simple_server.make_server(args['host'], args['port'], application)
    
    try:
        if args['mountpoint'] is None: args['mountpoint'] = ''
        print 'Bring up server at http://%s:%s%s' % (args['host'], args['port'], args['mountpoint'])
        while 1:
            server.handle_request()
    except KeyboardInterrupt:
        sys.exit()
    
        
    
