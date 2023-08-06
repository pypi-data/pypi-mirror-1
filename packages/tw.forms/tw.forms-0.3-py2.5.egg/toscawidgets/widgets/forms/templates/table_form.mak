<%namespace name="tw" module="toscawidgets.mako_util"/>\
<form ${tw.attrs(
    [('id', context.get('id')),
     ('name', name),
     ('action', action),
     ('method', method),
     ('class', css_class)],
    attrs=attrs
)}>
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
    <table border="0" cellspacing="0" cellpadding="2" ${tw.attrs(attrs=table_attrs)}>
        % for i, field in enumerate(ifields):
        <tr class="${i%2 and 'odd' or 'even'}" id="${field.id}.container" \
                ${tw.attrs(args_for(field).get('container_attrs') or field.container_attrs)}>\
            <%
                required = ['',' required'][int(field.is_required)]
                error = error_for(field)
                label_text = field.label_text
                help_text = field.help_text
            %>
            % if show_labels:
                <td class="labelcol">
                    <label ${tw.attrs(
                        [('id', '%s.label' % field.id),
                         ('for', field.id),
                         ('class', 'fieldlabel%s' % required)]
                    )}>${tw.content(label_text)}</label>
                </td>
            % endif
            <td>
                ${field.display(value_for(field), **args_for(field))}
                % if help_text:
                <span class="fieldhelp">${tw.content(help_text)}</span>
                % endif
                % if show_children_errors and error and not field.show_error:
                <span class="fielderror">${tw.content(error)}</span>
                % endif
            </td>
        </tr>
        % endfor
    </table>
    % if error and not error.error_dict:
    <span class="fielderror">${tw.content(error)}</span>
    % endif
</form>\
