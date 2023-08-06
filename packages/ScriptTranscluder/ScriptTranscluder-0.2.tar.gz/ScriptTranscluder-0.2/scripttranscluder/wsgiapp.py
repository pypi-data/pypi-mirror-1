from paste.deploy.converters import asbool
from scripttranscluder.app import ScriptTranscluder

def make_app(
    global_conf,
    same_host=True,
    allowed_urls=None,
    cache_dir=None):
    same_host = asbool(same_host)
    if isinstance(allowed_urls, basestring):
        allowed_urls = allowed_urls.split()
    return ScriptTranscluder(same_host=same_host,
                             allowed_urls=allowed_urls or [],
                             cache_dir=cache_dir or None)
