<%namespace file="/templates/base_xml.mak" import="*"/>
<graph ${attrs_list(attrs)} >\
    %for d in data:
    ${tostring(d)}\
    %endfor
%if trendlines:
    <trendLines>\
        %for l in trendlines:
        ${tostring(l)}\
        %endfor
    </trendLines>\
%endif
</graph>