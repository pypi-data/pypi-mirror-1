import cherrypy

from turbogears import widgets

class Analytics(widgets.Widget):
    template = """
    <div py:strip="True" xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/">

<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
</script>
<script type="text/javascript">
_uacct = "$analytics_key";
urchinTracker();
</script>
        
    </div>
    """
    params = ['analytics_key']
    params_doc = {'analytics_key': 'Google Analytics Key'}

    location = widgets.js_location.bodybottom

    def retrieve_javascript(self):
        if not self.analytics_key:
            return []
        else:
            return widgets.set_with_self(self)

    def add_for_location(self, location):
        return location == self.location

analytics_key = cherrypy.config.get("analytics.key", None)
analytics_js = Analytics(analytics_key = analytics_key)
