VERSION = (0, 1, 0, 'pre1')

def version():
    return '%s.%s.%s-%s' % VERSION

def get_version():
    return 'django-ittybitty %s' % version()
