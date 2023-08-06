from paste import urlparser


def make_app(global_conf={}):
    return urlparser.make_pkg_resources(global_conf,
                                        'ClueDojo',
                                        'cluedojo/static')
