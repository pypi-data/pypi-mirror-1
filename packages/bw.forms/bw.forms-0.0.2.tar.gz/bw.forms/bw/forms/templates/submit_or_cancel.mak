<%namespace name="tw" module="tw.core.mako_util"/>\

<% submit_img_tag = "" %>
% if submit_img_src is not None:
    <% submit_img_tag = '<img src="%s" />' % submit_img_src %>
% endif

<button ${tw.attrs(
    [('type', 'submit'),
     ('name', name),
     ('class', submit_css_class),
     ('id', context.get('id'))],
    attrs=attrs
)}>${submit_img_tag} ${submit_text}</button>\

<% cancel_img_tag = "" %>
% if cancel_img_src is not None:
    <% cancel_img_tag = '<img src="%s" />' % cancel_img_src %>
% endif

<a ${tw.attrs(
    [('class', cancel_css_class),
     ('href', cancel_url)],
    attrs=attrs
)}>${cancel_img_tag} ${cancel_text}</a>\
