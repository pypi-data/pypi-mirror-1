<%namespace name="tw" module="toscawidgets.mako_util"/>\
<textarea ${tw.attrs(
    [('id', context.get('id')),
     ('name', name),
     ('class', css_class)],
    attrs=attrs
    )}>\
${tw.content(value)}\
</textarea>\
