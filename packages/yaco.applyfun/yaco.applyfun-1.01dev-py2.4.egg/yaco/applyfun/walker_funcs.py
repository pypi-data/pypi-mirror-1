""" Use this module in combination with walker.py.
    Each function you define here and add to the functions dict,
    will be available as an option in the @@applyfun zope3 view.
"""

functions = {}

def list_children(ob, logger=None):
    """
    Example function to demonstrate the use of the httplogger.
    args:
    none
    """
    if logger:
        path = '/'.join(ob.getPhysicalPath())
        if 'menu' not in path:
            logger.log(path)
        else:
            logger.log(path, color='blue')

functions['List children'] = list_children

