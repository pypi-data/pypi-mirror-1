function setMenuImageHandlers() {
	jq(".menu-link").each( function() {
		var t= jq(this);		
		var hoverImage = t.find(".hover-image");
		var normalImage = t.find(".normal-image");
						
		t.bind("mouseenter", function(e) {
			normalImage.css("display", "none");
			hoverImage.css("display", "inline");
			return true;
		});

		t.bind("mouseleave", function(e) {
			normalImage.css("display", "inline");
			hoverImage.css("display", "none");		
			return true;			
		});
	});
}

//jq(setMenuImageHandlers);

function fixStyles() {
	jq("p.grey-box").wrap('<div class="grey-box-wrapper"></div>');
	jq("table.twinapex-table").wrap('<div class="table-wrapper"></div>');	
}

// Hack .. move to a file
jq(fixStyles);
