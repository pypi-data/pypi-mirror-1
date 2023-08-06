import re, cgi, urllib

def parse_url(name):
    pattern = re.compile(r'''
            (?P<drivername>\w+)://
            (?:
                (?P<user>[^:/]*)
                (?::(?P<passwd>[^/]*))?
            @)?
            (?:
                (?P<host>[^/:]*)
                (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<db>.*))?
            '''
            , re.X)

    m = pattern.match(name)
    if m is not None:
        components = m.groupdict()
        if components['db'] is not None:
            tokens = components['db'].split('?', 2)
            components['db'] = tokens[0]
            query = (len(tokens) > 1 and dict(cgi.parse_qsl(tokens[1]))) or None
            if query is not None:
                query = dict((k.encode('ascii'), query[k]) for k in query)
        else:
            query = None
        components['query'] = query

        if components['passwd'] is not None:
            components['passwd'] = urllib.unquote_plus(components['passwd'])

        return components
    else:
        raise Exception(
            "Could not parse rfc1738 URL from string '%s'" % name)
