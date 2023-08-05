<div xmlns:py="http://purl.org/kid/ns#" id="${id}" class="${as_bar and 'yuimenubar yuimenubarnav' or 'yuimenu'}">
<div py:def="displayMenu(menuItems, infix)" class="bd">
	<ul class="first-of-type">
	<li py:for="i, menuitem in enumerate(menuItems)"
	    class="yuimenu${infix}item${i==0 and ' first-of-type' or ''}">
		<a href="${menuitem[1]}" class="yuimenu${infix}itemlabel">${menuitem[0]}</a>
		<div py:if="len(menuitem) == 3 and len(menuitem[2]) > 0" class="yuimenu">
			${displayMenu(menuitem[2], '')}
		</div>
	</li>
	</ul>
</div>
<div class="bd" py:content="displayMenu(entries, as_bar and 'bar' or '')"></div>

<script language="JavaScript" type="text/JavaScript">
YAHOO.util.Event.onContentReady("${id}", function(p_oEvent) {
	var oMenuBar${id} = new YAHOO.widget.MenuBar("${id}", {
				autosubmenudisplay:true,
				<span py:if="not as_bar" py:strip="">position: 'static',</span>
				hidedelay:750,
				lazyload:true
			});
	oMenuBar${id}.render();
} );
</script>
</div>