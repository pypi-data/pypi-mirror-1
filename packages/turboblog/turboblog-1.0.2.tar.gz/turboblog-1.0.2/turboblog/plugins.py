import pkg_resources

def get_sidebar_plugins():
    sidebar_plugins = []
    for entrypoint in \
            pkg_resources.iter_entry_points("turboblog.plugins.sidebar"):
        engine = entrypoint.load()
        sidebar_plugins += [ engine() ]
    return sidebar_plugins

