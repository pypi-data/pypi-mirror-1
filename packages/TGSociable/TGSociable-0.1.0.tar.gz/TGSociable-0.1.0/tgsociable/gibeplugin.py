try:
    from gibe.plugin import Plugin
except ImportError:
    Plugin = None

if Plugin:
    from tgsociable import SociableWidget

    class SociablePlugin(Plugin):
        def __init__(self):
            self.reconfigure()

        def reconfigure(self):
            extra_sites = {
                'muti': {
                    'favicon': 'http://muti.co.za/images/favicon.ico',
                    'url': 'http://muti.co.za/submit?url=PERMALINK&title=TITLE',
                },
            }

            self.tgsw = SociableWidget(extra_sites = extra_sites, active_sites = ['muti', 'del.icio.us'])

        def post_top_widgets(self, post, wl):
            wl.extend([self.tgsw])
