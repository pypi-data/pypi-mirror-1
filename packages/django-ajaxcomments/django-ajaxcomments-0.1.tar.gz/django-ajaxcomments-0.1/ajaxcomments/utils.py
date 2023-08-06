from django.utils import simplejson
from django import http
from django.contrib.comments.views import comments
from django.shortcuts import render_to_response
from django.contrib.comments.views.utils import next_redirect

import logging

def jsonify_if_ajax(func, request):
    """A decorator to intercept the details intended for the
    render_to_response and next_redirect functions, and encode them in JSON to
    pass to the Javascript callback. If the request is not Ajax, however, it
    falls back to the provided function. 
    """
    def wrapped(*args, **kwargs):
        if request.is_ajax():
            success = True
            json_errors = {}
    
            try:
                form = args[1]['form']
    
                if form.errors:
                    for error in form.errors:
                        json_errors.update({error: str(form.errors[error])})
                    success = False
            except TypeError:
                pass
    
            json_response = simplejson.dumps({
                'success': success,
                'errors': json_errors,
            })
    
            return http.HttpResponse(json_response, mimetype="application/json")
        else:
            return func(*args, **kwargs)
    return wrapped

def include_request(func):
    """Include the current request object by re-wrapping the render_to_response and
    next_redirect methods each time the view is called.
    """
    def wrapped(*args, **kwargs):
        request = args[0]
        comments.render_to_response = jsonify_if_ajax(render_to_response, request)
        comments.next_redirect = jsonify_if_ajax(next_redirect, request)
        
        return func(*args, **kwargs)
    return wrapped

comments.post_comment = include_request(comments.post_comment)
