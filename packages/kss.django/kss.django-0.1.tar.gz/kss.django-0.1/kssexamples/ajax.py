from datetime import datetime

from kss.django import kss_view

@kss_view
def time_of_day(request, commands):
    commands.core.replaceInnerHTML('#now', 'Python says its: ' + datetime.now().strftime("%x %X") )

