from django import http


def show_username(request):
    return http.HttpResponse(request.user.username)