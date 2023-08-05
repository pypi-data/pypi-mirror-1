import turbogears as tg
from turbogears import validators
from turbogears.widgets import WidgetsList, FileField, HiddenField, \
        TextField, SubmitButton, ResetButton, SingleSelectField, \
        TableForm
from turboblog.formdisplay import form_display
from tinymce import TinyMCE

class FileUploadFields(WidgetsList):
    thefile = FileField(name='file_obj', label=_('File to upload'),
        validator = validators.FieldStorageUploadConverter())
    bid = HiddenField(label=_('BlogId'), name="bid")


file_upload_form = TableForm(
        "FileUpload",
        fields = FileUploadFields(),
        action = "%s" % tg.url("/blog_admin/upload_file"),
        submit_text = _("Upload"),
        )

# Monkey patch our form instance to add this helper function
file_upload_form.display_with_params = form_display

mce_plugins = ['table', 'save', 'advhr', 'advimage', 'advlink',
        'emotions', 'iespell', 'insertdatetime', 'preview',
        'zoom', 'flash', 'searchreplace', 'print', 'contextmenu',
        'paste', 'directionality', 'fullscreen', 'noneditable']

mce_adv_fonts = ['Arial=arial', 'helvetica' , 
        'sans-serif;Courier New=courier new', 'courier','monospace']

theme_adv_bt3_add = ['emotions', 'iespell', 'flash', 'advhr', 'separator',
        'print', 'separator', 'ltr', 'rtl', 'separator', 'fullscreen']

class WritePostFields(WidgetsList):
    bid = HiddenField(name="bid")
    post_id = HiddenField(name="post_id")

    published = SingleSelectField(
            label = _('Published'),
            name = 'publication_state',
            options = [(0, _('No')),(1, _('Yes'))],
            default = 0
            )

    post_title = TextField(
        label = _('Title'),
        name = 'post_title',
        attrs = dict(size=50),
        default = _('A title for this post'))

    content = TinyMCE(
            name="content",
            label=_('Post Body'),
            new_options=dict(
                convert_urls=False,
                mode="textareas",
                theme="advanced",
                plugins="%s" % ','.join(mce_plugins),
                theme_advanced_buttons3_add_before="tablecontrols,separator",
                theme_advanced_buttons3_add=','.join(theme_adv_bt3_add),
                theme_advanced_resize_horizontal='true',
                theme_advanced_resizing='true',
                theme_advanced_toolbar_location="top",
                theme_advanced_toolbar_align="left",
                theme_advanced_path_location="bottom",
                theme_advanced_fonts=",".join(mce_adv_fonts),
                width="300"
                )
            )

    trackback_url = TextField(
            label = _('Trackback URL'),
            name = 'trackback_url',
            attrs = dict(size=50),
            default = '')

writepost_form = TableForm(
        name = "edit",
        fields = WritePostFields(),
        action = "%s" % tg.url('/blog_admin/save_post'),
        submit_text = _('Save'),
        disabled_fields = []
        )

# Monkey patch our form instance to add this helper function
writepost_form.display_with_params = form_display

# vim: expandtab tabstop=4 shiftwidth=4:
