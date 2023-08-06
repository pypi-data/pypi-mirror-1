<%namespace name="tw" module="toscawidgets.mako_util"/>\
<%
    error = context.get('error')
%>\
<fieldset ${tw.attrs(
    [('id', context.get('id')),
     ('class', css_class)],
    attrs=attrs
)}>
    <legend>${tw.content(legend)}</legend>
    % if error and show_error:
    <div class="fielderror">${tw.content(error)}</div>
    % endif
    <div>
        % for field in ihidden_fields:
            <%
                error = error_for(field)
            %>
            ${field.display(value_for(field), **args_for(field))}
            % if show_children_errors and error and not field.show_error:
            <span class="fielderror">${tw.content(error)}</span>
            % endif
        % endfor
    </div>
    <ul class="field_list" ${tw.attrs(attrs=list_attrs)}>
        % for i, field in enumerate(ifields):
        <li class="${i%2 and 'odd' or 'even'}">\
            <%
                required = ['',' required'][int(field.is_required)]
                error = error_for(field)
                label_text = field.label_text
                help_text = field.help_text
            %>
            % if label_text:
            <label ${tw.attrs(
                [('id', '%s.label' % field.id),
                 ('for', field.id),
                 ('class', 'fieldlabel%s' % required)]
            )}>${tw.content(label_text)}</label>
            % endif
            ${field.display(value_for(field), **args_for(field))}
            % if help_text:
            <span class="fieldhelp">${tw.content(help_text)}</span>
            % endif
            % if show_children_errors and error and not field.show_error:
            <span class="fielderror">${tw.content(error)}</span>
            % endif
        </li>
        % endfor
    </ul>
</fieldset>\
