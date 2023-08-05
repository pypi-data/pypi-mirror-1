<div xmlns:py="http://purl.org/kid/ns#">
<input type="text"
       name="${name}"
       class="${field_class}"
       id="${id}"
       value="${value}"
       py:attrs="attrs"
/>
<div id="${id}_container" class="yac_container"></div>
<script language="JavaScript" type="text/JavaScript">
	oACDS = new YAHOO.widget.DS_XHR("${search_controller}", ${result_schema});
	oACDS.scriptQueryParam = "${search_param}";
	oACDS.scriptQueryAppend = "tg_format=json";
	oAutoComp = new YAHOO.widget.AutoComplete("${id}","${id}_container", oACDS);
	oAutoComp.useShadow = true;
	oAutoComp.minQueryLength = 2;
</script>
</div>