<%namespace name="tw" module="tw.core.mako_util"/>\
<button ${tw.attrs(
    [('type', 'submit'),
     ('name', name),
     ('class', submit_css_class),
     ('id', context.get('id'))],
    attrs=attrs
)}><img src="${submit_img_src}" /> ${submit_text}</button>\
<a ${tw.attrs(
    [('class', cancel_css_class),
     ('href', cancel_url)],
    attrs=attrs
)}><img src="${cancel_img_src}" /> ${cancel_text}</a>\
