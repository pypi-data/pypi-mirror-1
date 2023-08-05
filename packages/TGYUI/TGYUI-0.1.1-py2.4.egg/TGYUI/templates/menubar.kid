<div xmlns:py="http://purl.org/kid/ns#" id="${id}" class="yuimenubar">
<div class="bd">
	<ul class="first-of-type">
	<li py:for="i, barmenu in enumerate(entries)"
	    class="yuimenubaritem${i==0 and ' first-of-type' or ''}">
		<a href="${barmenu[1]}">${barmenu[0]}</a>
		<div py:if="len(barmenu[2]) > 0" class="yuimenu">
			<div class="bd"><ul>
			<li py:for="j, submenu in enumerate(barmenu[2])"
			    class="yuimenuitem${i==0 and ' first-of-type' or ''}">
				<a href="${submenu[1]}">${submenu[0]}</a>
				<div py:if="len(submenu[2]) > 0" class="yuimenu">
					<div class="bd"><ul class="first-of-type">
						<li py:for="k, lowmenu in enumerate(submenu[2])"
						    class="yuimenuitem">
							<a href="${lowmenu[1]}">${lowmenu[0]}</a>
						</li>
					</ul></div>
				</div>
			</li>
			</ul></div>
		</div>
	</li>
	</ul>
</div>
<script language="JavaScript" type="text/JavaScript">
YAHOO.util.Event.onContentReady("${id}", function(p_oEvent) {
	var oMenuBar = new YAHOO.widget.MenuBar("${id}", {
				autosubmenudisplay:true,
				hidedelay:750,
				lazyload:true,
				effect:{
					effect:YAHOO.widget.ContainerEffect.FADE,
					duration:0.25
				}
			});
	oMenuBar.render();
} );
</script>
</div>