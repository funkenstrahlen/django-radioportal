from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'feeds', 'radioportal.feeds.urls', name="feeds"),
    host(r'api', 'radioportal.api.urls', name="api"),
    host(r'dashboard', 'radioportal.dashboard.urls', name="dashboard"),
    host(r'', 'radioportal.urls', name="www"),
)