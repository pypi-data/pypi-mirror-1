<%page cached="False"/>
<%
	chart_id = context.get('id')
%>
<div id="${chart_id}" class="fusioncharts">Chart</div>
<script type="text/javascript">
    var obj_${chart_id} = new FusionCharts("${swf_file}", "${chart_id}", "${width}", "${height}", "${int(debug_mode)}", "${int(register_with_js)}");
    %if chart_url:
        obj_${chart_id}.addParam('wmode', 'transparent');
        obj_${chart_id}.setDataURL("${chart_url}");
    %endif
    %if data_xml:
        obj_${chart_id}.setDataXML(${data_xml});
    %endif
    obj_${chart_id}.render("${chart_id}");
</script>
<div id="teste"/>
