import staticmedia


def nginx(fp=None, **options):
    directives = []
    for mount_point in staticmedia.get_mount_points():
        directives.append('location %s { alias %s; }' % mount_point)
    if fp:
        fp.write('\n'.join(directives))
    else:
        return '\n'.join(directives)


def apache(fp=None, **options):
    directives = []
    for mount_url, mount_path in staticmedia.get_mount_points():
        directives.append(
            'Alias "%s" "%s"' % (mount_url, mount_path))
        if 'diroptions' in options:
            directives.append(
                '<Directory "%s">Options %s</Directory>' % (
                     mount_path, options['diroptions']))
    if fp:
        fp.write('\n'.join(directives))
    else:
        return '\n'.join(directives)


def lighttpd(fp=None, **options):
    directives = []

    raise NotImplemented
    
    if fp:
        fp.write('\n'.join(directives))
    else:
        return '\n'.join(directives)
