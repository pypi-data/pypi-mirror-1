<%namespace name="tw" module="tw.core.mako_util"/>\
<button ${tw.attrs(
    [('type', context.get('type')),
     ('name', name),
     ('class', css_class),
     ('id', context.get('id'))],
    attrs=attrs
)}><img src="${img_src}" /> ${submit_text}</button>\
