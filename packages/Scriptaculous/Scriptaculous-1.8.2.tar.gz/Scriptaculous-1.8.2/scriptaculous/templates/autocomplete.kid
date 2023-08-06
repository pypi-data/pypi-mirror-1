<div xmlns:py="http://purl.org/kid/ns#">
	<input type="text"
	       name="${name}"
	       value="${value}"
	       id="${id}"
	       class="${field_class}"
	       py:attrs="attrs"/>
	<div id="${id}_choices" class="autocomplete"></div>
	<script language="JavaScript" type="text/JavaScript">
		new Ajax.Autocompleter("${id}", "${id}_choices", "${search_controller}",
			{paramName: "${search_param}", minChars: ${min_chars}});
	</script>
</div>