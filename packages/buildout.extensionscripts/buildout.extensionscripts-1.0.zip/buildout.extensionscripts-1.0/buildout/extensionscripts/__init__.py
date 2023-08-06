def extension(buildout=None):
    import imp, os
    scripts = buildout.get('buildout', {}).get('extension-scripts', '').split('\n')
    for script in scripts:
        if not script.strip():
            continue
        filename, function = script.split(':')
        filename = os.path.abspath(filename.strip())
        module = imp.load_source('script', filename)
        getattr(module, function.strip())(buildout)
