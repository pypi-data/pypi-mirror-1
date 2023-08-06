from repoze.bfg import make_app
from repoze.bfg import get_options

def app(global_config, **kw):
    # paster app config callback
    from bestappever.models import get_root
    import bestappever
    return make_app(get_root, bestappever, options=get_options(kw))

if __name__ == '__main__':
    from paste import httpserver
    httpserver.serve(app(None), host='0.0.0.0', port='6543')
    
