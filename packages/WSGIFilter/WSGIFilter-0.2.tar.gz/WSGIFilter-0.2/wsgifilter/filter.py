import re
from paste.response import header_value

class Filter(object):
    """
    Class that implements WSGI output-filtering middleware
    """

    # If this is true, then conditional requests will be diabled
    # (e.g., If-Modified-Since)
    force_no_conditional = True
    
    conditional_headers = [
        'HTTP_IF_MODIFIED_SINCE',
        'HTTP_IF_NONE_MATCH',
        'HTTP_ACCEPT_ENCODING',
        ]

    # If true, then any status code will be filtered; otherwise only
    # 200 OK responses are filtered
    filter_all_status = False

    # If you provide this (a string or list of string mimetypes) then
    # only content with this mimetype will be filtered
    filter_content_types = ('text/html', )

    # If this is set, then HTTPEncode will be used to decode the value
    # given provided mimetype and this output
    format_output = None

    # You can also use a specific format object, which forces the
    # parsing with that format
    format = None

    # If you aren't using a format but you want unicode instead of
    # 8-bit strings, then set this to true
    decode_unicode = False

    # When we get unicode back from the filter, we'll use this
    # encoding and update the Content-Type:
    output_encoding = 'utf8'

    def __init__(self, app):
        self.app = app
        if isinstance(self.format, basestring):
            from httpencode import get_format
            self.format = get_format(self.format)
        if (self.format is not None
            and self.filter_content_types is Filter.filter_content_types):
            self.filter_content_types = self.format.content_types

    def __call__(self, environ, start_response):
        if self.force_no_conditional:
            for key in self.conditional_headers:
                if key in environ:
                    del environ[key]
        # @@: I should actually figure out a way to deal with some
        # encodings, particular since stuff we don't care about like
        # text/javascript could be gzipped usefully.
        if 'HTTP_ACCEPT_ENCODING' in environ:
            del environ['HTTP_ACCEPT_ENCODING']
        shortcutted = []
        captured = []
        written_output = []
        def replacement_start_response(status, headers, exc_info=None):
            if not self.should_filter(status, headers, exc_info):
                shortcutted.append(None)
                return start_response(status, headers, exc_info)
            if exc_info is not None and shortcutted:
                raise exc_info[0], exc_info[1], exc_info[2]
            # Otherwise we don't care about exc_info...
            captured[:] = [status, headers]
            return written_output.append
        app_iter = self.app(environ, replacement_start_response)
        if shortcutted:
            # We chose not to filter
            return app_iter
        if not captured or written_output:
            # This app hasn't called start_response We can't do
            # anything magic with it; or it used the start_response
            # writer, and we still can't do anything with it
            try:
                for chunk in app_iter:
                    written_output.append(chunk)
            finally:
                if hasattr(app_iter, 'close'):
                    app_iter.close()
            app_iter = written_output
        try:
            return self.filter_output(
                environ, start_response,
                captured[0], captured[1], app_iter)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()

    def paste_deploy_middleware(cls, app, global_conf, **app_conf):
        # You may wish to override this to make it convert the
        # arguments or use global_conf.  To declare your entry
        # point use:
        # setup(
        #   entry_points="""
        #   [paste.filter_app_factory]
        #   myfilter = myfilter:MyFilter.paste_deploy_middleware
        #   """)
        return cls(app, **app_conf)

    paste_deploy_middleware = classmethod(paste_deploy_middleware)

    def should_filter(self, status, headers, exc_info):
        if not self.filter_all_status:
            if not status.startswith('200'):
                return False
        content_type = header_value(headers, 'content-type')
        if content_type and ';' in content_type:
            content_type = content_type.split(';', 1)[0]
        if content_type in self.filter_content_types:
            return True
        return False

    _charset_re = re.compile(
        r'charset="?([a-z0-9-_.]+)"?', re.I)

    # @@: I should do something with these:
    #_meta_equiv_type_re = re.compile(
    #    r'<meta[^>]+http-equiv="?content-type"[^>]*>', re.I)
    #_meta_equiv_value_re = re.compile(
    #    r'value="?[^">]*"?', re.I)
    
    def filter_output(self, environ, start_response,
                      status, headers, app_iter):
        content_type = header_value(headers, 'content-type')
        if ';' in content_type:
            content_type = content_type.split(';', 1)[0]
        if self.format_output:
            import httpencode
            format = httpencode.registry.find_format_match(self.format_output, content_type)
        else:
            format = self.format
        if format:
            data = format.parse_wsgi_response(status, headers, app_iter)
        else:
            data = ''.join(app_iter)
            if self.decode_unicode:
                # @@: Need to calculate encoding properly
                full_ct = header_value(headers, 'content-type') or ''
                match = self._charset_re.search(full_ct)
                if match:
                    encoding = match.group(1)
                else:
                    # @@: Obviously not a great guess
                    encoding = 'utf8'
                data = data.decode(encoding, 'replace')
        new_output = self.filter(
            environ, headers, data)
        if format:
            app = format.responder(new_output, headers=headers)
            app_iter = app(environ, start_response)
            return app_iter
        else:
            enc_data = []
            encoding = self.output_encoding
            if not isinstance(new_output, basestring):
                for chunk in new_output:
                    if isinstance(chunk, unicode):
                        chunk = chunk.encode(encoding)
                    enc_data.append(chunk)
            elif isinstance(new_output, unicode):
                enc_data.append(new_output.encode(encoding))
            else:
                enc_data.append(new_output)
            start_response(status, headers)
            return enc_data

    def filter(self, environ, headers, data):
        raise NotImplementedError
