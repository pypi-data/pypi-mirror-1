from repoze.bfg.chameleon_zpt import render_template_to_response

def my_view(context, request):
    return render_template_to_response('templates/mytemplate.pt',
                                       request = request,
                                       project = 'MyProject')
