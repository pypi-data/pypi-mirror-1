<%namespace name="tw" module="toscawidgets.mako_util"/>\
<div ${tw.attrs(
    [('id', context.get('id')),
     ('class', css_class)],
    attrs=attrs
    )}>\
$text
</div>\
