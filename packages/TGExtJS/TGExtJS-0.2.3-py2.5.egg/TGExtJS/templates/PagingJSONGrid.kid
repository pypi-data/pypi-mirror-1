<div xmlns:py="http://purl.org/kid/ns#" id="${id}_container">
<!--! begin: blue box -->
	<div id="${id}_panel" style="width: ${width}; height: ${height};">
	<div id="${id}"></div>
	</div>
<!--! end: blue box -->
	<script type="text/javascript">
		Ext.onReady(json_grid_from_url_values('${id}', '${data_url}', ${limit}, '${property_url}'));
	</script>
<!--! end: init-script -->
</div>