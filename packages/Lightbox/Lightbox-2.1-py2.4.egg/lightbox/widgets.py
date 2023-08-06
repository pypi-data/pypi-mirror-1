__all__ = [
    'default_config',
    'Lightbox',
    'LightboxConfig',
    'lightbox_js',
    'lightbox_css',
]

import pkg_resources

from scriptaculous import prototype_js, scriptaculous_js

from turbogears import url
from turbogears.widgets import CSSLink, JSLink, Widget, WidgetDescription, \
                               register_static_directory, JSSource

static_dir = pkg_resources.resource_filename("lightbox", "static")
register_static_directory("lightbox", static_dir)

lightbox_js = JSLink("lightbox", "javascript/lightbox.js")
lightbox_css = CSSLink("lightbox", "css/lightbox.css", media="screen")

class LightboxConfig(JSSource):
    """Widget for inserting the Lightbox configuration JavaScript into the page.

    See parameter description for available configuration options.
    """

    template = """
<script type="text/javascript">
    var LightboxOptions = {
        fileLoadingImage: "${loading_img_url}",
        fileBottomNavCloseImage:"${close_img_url}",
        overlayOpacity: ${overlay_opacity},
        animate: "${animate}",
        resizeSpeed: ${resize_speed},
        borderSize: ${border_size},
        labelImage: "${label_image}",
        labelOf: "${label_of}"
    };
</script>
"""

    params = ["overlay_opacity", "animate", "resize_speed", "border_size",
        "label_image", "label_of"]
    overlay_opacity = 0.8
    animate = 'true'
    resize_speed = 7
    border_size = 10
    label_image = "Image"
    label_of = "of"

    params_doc = {
        'overlay_opacity': 'Controls transparency of shadow overlay '
            '(0.0 - 1.0, default: 0.8)',
        'animate': 'Toggles resizing animations'
            '("true" or "false", default: "true")',
        'resize_speed': 'Controls the speed of the image resizing animations '
            '(1=slowest and 10=fastest, default: 7)',
        'border_size': 'If you adjust the padding in the CSS, you will also '
            'need to specify this setting (default: 10)',
        'label_image': 'Term to use for "Image" part of "Image # of #" label. '
            'Change it for non-english localization.',
        'label_of': 'Term to use for "of" part of "Image # of #" label. '
            'Change it for non-english localization.'
    }

    def __init__(self, **params):
        super(LightboxConfig, self).__init__("dummy", **params)

    def update_params(self, d):
        super(LightboxConfig, self).update_params(d)
        d["static"] =  url("/tg_widgets/lightbox/")
        d.setdefault('loading_img_url', d["static"] + 'images/loading.gif')
        d.setdefault('close_img_url', d["static"] + 'images/closelabel.gif')

default_config = LightboxConfig()

class Lightbox(Widget):
    """Widget that creates a Lightbox photo viewer.

    The value should be the URL of the main image to display. You also need to
    pass in 'thumb_url', 'thumb_width' and 'thumb_height' to specify the
    thumbnail image that will be displayed (see also the parameter description).
    """

    template = """\
<a xmlns:py="http://purl.org/kid/ns#" href="${value}" rel="${rel}" py:attrs="dict(title=title)"><img src="${thumb_url}" width="${thumb_width}" height="${thumb_height}" border="0"/></a>
"""

    params = ['group', 'rel', 'thumb_url', 'thumb_width', 'thumb_height',
        'title']
    thumb_url = ''
    thumb_width = 80
    thumb_height = 60
    title = None
    group = None
    rel = 'lightbox'

    params_doc = {
        'thumb_url': 'URL of thumbnail image (required)',
        'thumb_width': 'Width of thumbnail image (required)',
        'thumb_height': 'Height of thumbnail image (required)',
        'title': 'Caption to show below image (optional)',
        'group': 'Name of group of related images. You can browse through all '
            'Lightbox images in the same group in one popup (optional).'
    }

    def __init__(self, config=default_config, css=lightbox_css, **params):
        if isinstance(css, Widget):
            css = [css]
        self.css = css
        self.javascript = [prototype_js, scriptaculous_js, lightbox_js, config]
        super(Lightbox, self).__init__(**params)

    def update_params(self, d):
        super(Lightbox, self).update_params(d)
        if d['group']:
            d['rel'] += '[%s]' % d['group']

class LightboxConfigDesc(WidgetDescription):
    name = "Lightbox configuration"
    for_widget = LightboxConfig()
    template = "<div>Configuration for the Lightbox widget.</div>"
    full_class_name = "lightbox.LightboxConfig"


class LightboxDesc(WidgetDescription):
    name = "Lightbox demo"
    for_widget = Lightbox()
    show_separately = True

    template = """
<div>
${for_widget.display(static + "images/image-1.jpg", thumb_url=static + "images/thumb-1.jpg", thumb_width=100, thumb_height=40, title="Just a sample image", group="mygroup")}
${for_widget.display(static + "images/image-3.jpg", thumb_url=static + "images/thumb-3.jpg", thumb_width=100, thumb_height=40, title="Another sample", group="mygroup")}
${for_widget.display(static + "images/image-4.jpg", thumb_url=static + "images/thumb-4.jpg", thumb_width=100, thumb_height=40, title="That's it", group="mygroup")}
</div>"""

    def update_params(self, d):
        super(LightboxDesc, self).update_params(d)
        d["static"] = url("/tg_widgets/lightbox/")
