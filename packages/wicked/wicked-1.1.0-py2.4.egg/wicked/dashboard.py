import pkg_resources

BASE_OPTIONS="wicked.base_registration"
CACHE_OPTIONS="wicked.cache_manager"

class WickedDashboard(object):
    """control panel for wicked manipulation"""

    def __init__(self, context, request):
        self.context = context
        self.request = request





