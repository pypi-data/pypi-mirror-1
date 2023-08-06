def make_app(global_conf, config_file):
    from mercurial import demandimport; demandimport.enable()
    from mercurial.hgweb.hgwebdir_mod import hgwebdir
    application = hgwebdir(config_file)
    return application
