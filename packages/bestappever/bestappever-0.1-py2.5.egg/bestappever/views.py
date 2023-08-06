from repoze.bfg.template import render_template_to_response

def my_view(context, request):
    return render_template_to_response('templates/mytemplate.pt',
                                       project = 'bestappever',
                                       abspath = context.absolute_path(),
                                       name = context.__name__)
