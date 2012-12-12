
from snack import settings
from snack.api.http import HTTPClient

WLEE_URL = settings.WLEE_URL

def get_instance_performance(instance_id):
    url = "%s/instance/%d/performance" % (WLEE_URL, instance_id)
    return HTTPClient().request(url, method="GET")[1]
    