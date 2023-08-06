<div xmlns:py="http://purl.org/kid/ns#" py:strip="">
	<input type="password"
	       name="${name}"
	       class="${field_class}"
	       id="${field_id}"
	       value="${value}"
	       onkeyup="updateStrength(this, this.nextSibling.firstChild)"
	       onfocus="updateStrength(this, this.nextSibling.firstChild)"
	       py:attrs="attrs"/><div class="psContainer"><div class="psStrength"></div></div>
</div>