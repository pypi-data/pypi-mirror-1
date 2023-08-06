/*
jQuery portletNavigationTree plugin
	Collapsible/expandable navigation tree.
*/

(function($) {
	// Expands or collapses a node of which sub-items already have been loaded.
	function toggleNode(event){
		var twistie = $(this);
		
		// find ul element
		var ul = $(this).closest("li").children("ul");
		if (!ul) { return; }
		
		// toggle class names
		if (twistie.hasClass("showChildren")){
			ul.removeClass("hideChildren");
			twistie.removeClass("showChildren");
		} else {
			ul.addClass("hideChildren");
			twistie.addClass("showChildren");
		}
		
		// prevent default action of event
		event.preventDefault();
	}
	
	// Loads the sub-items of a node.
	function loadNode(event){
	
		// prevent default action of event
		event.preventDefault();
		
		// Find the portlet information
		var portletWrapper = $(this).closest(".portletWrapper");
		var portletHash = portletWrapper[0] ? portletWrapper[0].id.replace("portletwrapper-","") : "";
		if (!portletHash) { return; }

		// find the li element of the clicked node
		var node = $(this).closest("li");
		
		if (node.hasClass("nodeLoading")) { return; }
		
		// get node uid
		var uidClassName = node[0].className.match(/node-(\w+)/);
		var uid = uidClassName ? uidClassName[1] : null;
		if (!uid) { return; }
		
		// data to send with request
		var data = {
			portlethash : portletHash,
			uid : uid
		};
		
		// add nodeLoading class
		node.addClass("nodeLoading");
		
		// send request
		$.post("expandNode", data, function(html){
			node.replaceWith(html);
		});
	}

	// observe clicks on toggle buttons
	$(".portletNavigationTree span.toggleNode").live("click", loadNode);
	$(".portletNavigationTree span.expandedNode").live("click", toggleNode);
})(jQuery);
