import sys
import testing

def paste_deploy_app(global_conf, full_stack=True, **app_conf):

    def pdWsgiApp (environ,start_response):
        return wsgiHandler(environ,start_response)
    
    return pdWsgiApp

def wsgiHandler (environ, start_response):

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''
<html>
<body>
<title>Hello %(subject)s</title>
    <p>Hello %(subject)s!</p>
    <p>SCRIPT_NAME:%(script_name)s <br>
    PATH_INFO:%(path_info)s <p>
    SYS_PATH: %(sys_path)s <p>
</body>
'''
    %  {'subject': 'world' , 'script_name' : environ['SCRIPT_NAME'], 'path_info' : environ['PATH_INFO'], 'sys_path' : sys.path,  }]
