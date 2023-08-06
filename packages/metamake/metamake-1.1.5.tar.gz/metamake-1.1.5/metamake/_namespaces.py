_current_namespace = []

def get_current_namespace():
    return _current_namespace

def namespace(method=None):
    
    def decorate(method):
        global _current_namespace
        old_namespace = list(_current_namespace)
        _current_namespace += [method]

        # define all the subtasks
        method()

        _current_namespace = old_namespace
        return method
        
    if method == None:
        def subdecorator(method):
            return decorate(method)
        return subdecorator
    else:
        return decorate(method)
