var LinkCollection = { };
// Height of the tallest document which has been displayed
LinkCollection.maxheight = 0;

LinkCollection.render_doc = function render_doc(node, uid) {
    jq('a.current-linklist-item').removeClass('current-linklist-item');
    jq(node).addClass('current-linklist-item');

    jq('div.prefetched-docs').each(
	function(i){
	    if (jq(this).is(':visible')) {
		jq(this).hide();
	    }
	}
    );

    var doc = jq('div#doc-'+uid);
    doc.fadeIn(300);

    /* Prevent the page from jumping up and down for long and short
    documents by setting the height of the current doc to the
    height of the largest doc displayed so far. */
    if (doc.height() > LinkCollection.maxheight) {
    	LinkCollection.maxheight = doc.height();
    }
    doc.height(LinkCollection.maxheight);

    // Scroll to the top of the linkbox
    linkbox=jq('div#slc-linkcollection-linkbox');
    linkboxtop=linkbox.offset().top;
    body=jq('html,body');
    body.scrollTop(linkboxtop);
    return false;
}
