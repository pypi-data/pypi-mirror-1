from mercurial.hgweb.hgwebdir_mod import hgwebdir
from mercurial.hgweb.hgweb_mod import hgweb

def hgwebdir_app_factory(global_config, **local_conf):
    return hgwebdir(local_conf.get('webdir.conf', None))

def hgweb_app_factory(global_config, **local_conf):
    return hgweb(local_conf.get("repository", '.'))
