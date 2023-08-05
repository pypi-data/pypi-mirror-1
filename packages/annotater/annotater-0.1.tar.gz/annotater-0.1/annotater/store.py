"""Annotation storage.

TODO:

1. Move to templates for annotater store forms (?)
"""
import os
import logging

import paste.request

from routes import *

# annotater stuff
import annotater.model


class AnnotaterStore(object):
    "Application to provide 'annotation' store."

    DEBUG = True

    def __init__(self, service_path='annotation'):
        """Create the WSGI application.

        @param service_path: offset url where this application is mounted.
            Should be specified without leading or trailing '/'.
        """
        self.service_path = service_path
        self.logger = self.setup_logging()

    def get_routes_mapper(self):
        # some extra additions to standard layout from map.resource
        # help to make the url layout a bit nicer for those using the web ui
        map = Mapper()
        map.connect(self.service_path + '/delete/:id',
                controller='annotation',
                action='delete',
                conditions=dict(method=['GET']))
        map.connect(self.service_path + '/edit/:id',
                controller='annotation',
                action='edit',
                conditions=dict(method=['GET']))

        map.resource(self.service_path, self.service_path)

        # map.resource assumes PUT for update but marginalias uses POST the
        # exact mappings for REST seems a hotly contested matter see e.g.
        # http://www.megginson.com/blogs/quoderat/archives/2005/04/03/post-in-rest-create-update-or-action/
        # must have this *after* map.resource as otherwise overrides the create
        # action
        map.connect(self.service_path + '/:id',
                controller='annotation',
                action='update',
                conditions=dict(method=['POST']))
        return map

    def setup_logging(self):
        level = logging.DEBUG
        logger = logging.getLogger('annotater')
        logger.setLevel(level)
        log_file_path = 'annotater-debug.log'
        fh = logging.FileHandler(log_file_path, 'w')
        fh.setLevel(level)
        logger.addHandler(fh)
        logger.info('START LOGGING')
        return logger

    def __call__(self, environ, start_response):
        self.environ = environ
        self.map = self.get_routes_mapper()
        self.map.environ = environ
        self.start_response = start_response
        self.path = environ['PATH_INFO']
        self.mapdict = self.map.match(self.path)
        action = self.mapdict['action']
        self.anno_schema = annotater.model.AnnotationSchema()
        if action != 'delete':
            self.query_vals = paste.request.parse_formvars(self.environ)
        else: 
            # DELETE from js causes paste.request.parse_formvars to hang since
            # we do not need it for delete if using clean urls just skip
            # TODO: find out why this is and fix it.
            self.query_vals = {}

        if self.DEBUG:
            self.logger.debug('** CALL TO ANNOTATE')
            self.logger.debug('path: %s' % self.path)
            self.logger.debug('environ: %s' % environ)
            self.logger.debug('mapdict: %s' % self.mapdict)
            self.logger.debug('query_vals: %s' % self.query_vals)


        if action == 'index':
            return self.index()
        elif action == 'new':
            return self.new()
        elif action == 'create':
            return self.create()
        elif action == 'edit':
            return self.edit()
        elif action == 'update':
            return self.update()
        elif action == 'delete':
            return self.delete()
        else:
            status = '404 Not Found'
            response_headers = [ ('Content-type', 'text/plain'), ]
            self.start_response(status, response_headers)
            return ['Not found or method not allowed']


    def _make_annotate_form(self, form_name, action_url, form_defaults):
        from formencode import htmlfill
        keys = [ 'url' , 'range', 'note' ]
        vals = {}
        for key in keys:
            vals[key] = form_defaults.get(key, '')
        formfields = ''
        for key in keys:
            formfields += \
'''            <label for="%s">%s:</label><input name="%s" id="%s" /><br />
''' % (key, key, key, key)
            
        form = \
'''<html>
    <head></head>
    <body>
        <form name="%s" action="%s" method="POST">
           %s
           <input type="submit" name="submission" value="send the form" />
       </form>
    </body>
</html>''' % (form_name, action_url, formfields)
        
        form = htmlfill.render(form, vals)
        return form

    def index(self):
        format = self.query_vals.get('format', 'html')
        status = '200 OK'
        response_headers = [ ('Content-type', 'text/html') ]
        result = ''
        if format == 'html':
            result = annotater.model.Annotation.list_annotations_html()
            result = \
'''<html>
<head>
    <title>Annotations</title>
</head>
<body>
    %s
</body>
</html>''' % (result)
        elif format == 'atom':
            response_headers = [ ('Content-type', 'application/xml') ]
            result = annotater.model.Annotation.list_annotations_atom()
        else:
            status = '500 Internal server error'
            result = 'Unknown format: %s' % format
        self.start_response(status, response_headers)
        return [result]
    
    def new(self):
        status = '200 OK'
        response_headers = [
                ('Content-type', 'text/html'),
                ]
        posturl = self.map.generate(controller='annotation', action='create')
        form = \
'''<html>
<head></head>
<body>
    <form name='annotation_create' action="%s" method="POST">
       <label>url:</label> <input name="url" id="url" /><br />
       <label>range:</label><input name="range" id="range" /><br />
       <label>note:</label><input name="note" id="note" /><br />
       <input type="submit" name="submission" value="send the form" />
   </form>
</body>
</html>''' % posturl
        self.start_response(status, response_headers)
        return [ form ]

    def create(self):
        url = self.query_vals.get('url')
        range = self.query_vals.get('range', 'NO RANGE')
        note = self.query_vals.get('note', 'NO NOTE')
        anno = annotater.model.Annotation(
                url=url,
                range=range,
                note=note)
        status = '201 Created'
        location = '/annotation/%s' % anno.id
        response_headers = [
                ('Content-type', 'text/html'),
                ('Location', location)
                ]
        self.start_response(status, response_headers)
        return ['']

    def edit(self):
        id = self.mapdict['id']
        try:
            id = int(id)
        except:
            status = '400 Bad Request'
            response_headers = [
                ('Content-type', 'text/html'),
                ]
            self.start_response(status, response_headers)
            msg = '<h1>400 Bad Request</h1><p>No such annotation #%s</p>' % id
            return [msg]
        anno = annotater.model.Annotation.get(id)
        posturl = self.map.generate(controller='annotation',
                action='update', id=anno.id, method='POST')
        print 'Post url:', posturl
        form_defaults = self.anno_schema.from_python(anno)
        form = self._make_annotate_form('annotate_edit', posturl,
                form_defaults)
        status = '200 OK'
        response_headers = [
                ('Content-type', 'text/html'),
                ]
        self.start_response(status, response_headers)
        return [ form ]

    def update(self):
        id = self.mapdict['id']
        try:
            id = int(id)
        except:
            status = '400 Bad Request'
            response_headers = [
                ('Content-type', 'text/html'),
                ]
            self.start_response(status, response_headers)
            msg = '<h1>400 Bad Request</h1><p>No such annotation #%s</p>' % id
            return [msg]
        new_values = dict(self.query_vals)
        new_values['id'] = id
        if new_values.has_key('submission'): # comes from post
            del new_values['submission']
        else: # comes direct from js
            # as comes from js need to add in the existing values for to_python
            # this is a bit of a hack but it the easiest way i can think of to
            # merge the values
            current = annotater.model.Annotation.get(id)
            current_defaults = self.anno_schema.from_python(current)
            for key in current_defaults.keys():
                if not new_values.has_key(key):
                    new_values[key] = current_defaults[key]
            # remove attributes coming from js that we do not yet support
            del new_values['access']
        anno_edited = self.anno_schema.to_python(new_values)
        status = '204 Updated'
        response_headers = []
        self.start_response(status, response_headers)
        return ['']

    def delete(self):
        id = self.mapdict['id']
        response_headers = [ ('Content-type', 'text/html'), ]
        if id is None:
            status = '400 Bad Request'
            response_headers = [ ('Content-type', 'text/html'), ]
            self.start_response(status, response_headers)
            return ['<h1>400 Bad Request</h1><p>Bad ID</p>']
        else:
            status = '204 Deleted'
            try:
                id = int(id)
                annotater.model.Annotation.delete(id)
                self.start_response(status, response_headers)
                return []
            except:
                status = '500 Internal server error'
                self.start_response(status, response_headers)
                return ['<h1>500 Internal Server Error</h1>Delete failed']
    
