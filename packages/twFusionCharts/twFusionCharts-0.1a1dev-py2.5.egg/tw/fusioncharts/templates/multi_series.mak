<%namespace file="/templates/base_xml.mak" import="*"/> \
<graph ${attrs_list(attrs)} >\
    <categories ${attrs_list(categories_attrs)} >\
        %for category in categories:
        <category ${attrs_list(category)} /> \
        %endfor
    </categories>\
    %for dataset in datasets:
    <dataset ${attrs_list(dataset.attrs)}>\
        %for d in dataset.data:
            ${tostring(d)}\
        %endfor
    </dataset>\
    %endfor
    %if trendlines:
    <trendLines>\
        %for l in trendlines:
        ${tostring(l)}\
        %endfor
    </trendLines>\
    %endif
</graph>