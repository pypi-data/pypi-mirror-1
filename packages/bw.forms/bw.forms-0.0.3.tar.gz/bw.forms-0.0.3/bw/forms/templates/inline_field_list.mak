<%namespace name="tw" module="tw.core.mako_util"/>\
    % for field in fields:
        <span ${tw.attrs(args_for(field).get('container_attrs') or field.container_attrs)}>\
            <%
                required = ['', ' required'][int(field.is_required)]
                required_star = field.is_required and ' <span class="req">*</span>' or ''
                error = error_for(field)
                label_text = field.label_text
                help_text = field.help_text
            %>

            % if label_text and not field.suppress_label:
            <label ${tw.attrs(
                [('id', '%s_label' % field.id),
                 ('for', field.id),
                 ('class', 'fieldlabel%s' % required)]
            )}>${label_text}${required_star}</label>
            % endif

            ${field.display(value_for(field), **args_for(field))}

            % if help_text and not hover_help:
            <span class="fieldhelp">${help_text}</span>
            % endif

            % if show_children_errors and error and not field.show_error:
            <span class="fielderror">${tw.content(error)}</span>
            % endif
        </span>
    % endfor
    <div style="clear: both;"></div>
