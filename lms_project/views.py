from django.shortcuts import render


def server_error(request, template_name='errors/500.html'):
    return render(request, template_name, status=500)


def page_not_found(request, exception):
    context = {
        'path': request.path
    }
    return render(request, 'errors/404.html', context, status=404)


def forbidden(request, exception):
    context = {
        'path': request.path
    }
    return render(request, 'errors/403.html', context, status=403)
