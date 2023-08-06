from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext, TemplateDoesNotExist

def direct_to_disk_template(request, template_name):
    ''' Load template by it's name. 
        Appends '.html' or '.htm' extension if needed.
    '''
    try:
        return render_to_response([
                                   'auto_urls/' + template_name,
                                   'auto_urls/' + template_name+'.html', 
                                   'auto_urls/' + template_name+'.htm',
                                   template_name, 
                                   template_name+'.html', 
                                   template_name+'.htm',
                                 ], {}, RequestContext(request))
    except TemplateDoesNotExist:
        raise Http404