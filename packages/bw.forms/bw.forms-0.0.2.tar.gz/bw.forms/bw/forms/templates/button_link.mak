<%namespace name="tw" module="tw.core.mako_util"/>\
<a ${tw.attrs(
    [('class', css_class),
     ('href', href)],
    attrs=attrs
)}><img src="${img_src}" /> ${submit_text}</a>\
