from django.http import HttpResponse

from kss.base import KSSCommands

def kss_response(commands):
    """ return http response prepared for kss """
    return HttpResponse(commands.render(), mimetype='text/xml')

def kss_view(func):
    def new_func(request, *args, **kwargs):
        commands = KSSCommands()
        # Let the view modify the commands object by adding commands
        # to it
        func(request, commands, *args, **kwargs)
        return kss_response(commands)
    return new_func
