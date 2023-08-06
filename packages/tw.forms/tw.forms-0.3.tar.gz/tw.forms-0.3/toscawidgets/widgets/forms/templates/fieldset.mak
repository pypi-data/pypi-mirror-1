<%namespace name="tw" module="toscawidgets.mako_util"/>\
<fieldset ${tw.attrs(
    [('id', context.get('id')),
     ('class', css_class)],
    attrs=attrs
)}>
    <legend>${tw.content(legend)}</legend>
    % for field in ihidden_fields:
        ${field.display(value_for(field), **args_for(field))}
    % endfor
    % for field in ifields:
        ${field.display(value_for(field), **args_for(field))} <br />
    % endfor
</fieldset>\
