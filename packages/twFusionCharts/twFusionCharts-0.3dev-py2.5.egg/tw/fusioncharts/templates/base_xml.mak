<%!
    from xml.etree.ElementTree import tostring
%> \
<%def name="tostring(x)"> \
${tostring(x)}\
</%def>

<%def name="attrs_list(attrs)"> \
%for k,v in attrs.items(): 
 ${k}='${v}' \
%endfor
</%def>