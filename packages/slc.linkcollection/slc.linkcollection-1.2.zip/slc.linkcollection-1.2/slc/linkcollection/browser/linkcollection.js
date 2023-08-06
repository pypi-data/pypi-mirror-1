
function render_doc(node, uid) {
    jq('a.current-linklist-item').removeClass('current-linklist-item'); 
    jq(node).addClass('current-linklist-item'); 
    jq('div.prefetched-docs').each(
        function(i){
            if (jq(this).is(':visible')) 
                jq(this).hide();
        }
    ); 
    nid = 'div#doc-'+uid;
    jq(nid).fadeIn(300); 
    return false;
}
