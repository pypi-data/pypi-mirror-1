from paste import urlparser


def get_google_block(environ):
    base_url = 'http://ajax.googleapis.com/ajax/libs/dojo/1.3'
    return '''
<script type="text/javascript" src="%(base_url)s/dojo/dojo.xd.js"></script>
<link rel="stylesheet" href="%(base_url)s/dijit/themes/tundra/tundra.css"
      type="text/css" media="screen" title="dijit tundra css" charset="utf-8">
''' % {'base_url': base_url}


def make_app(global_conf={}):
    return urlparser.make_pkg_resources(global_conf,
                                        'ClueDojo',
                                        'cluedojo/static')
