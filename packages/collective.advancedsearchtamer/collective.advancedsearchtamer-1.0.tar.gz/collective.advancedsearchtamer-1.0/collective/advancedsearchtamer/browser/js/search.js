jq(document).ready(function() {
    if (!jq('body.template-search_form').size()) {
	return;
    }

    HalfwayHouse = {}    
    HalfwayHouse.options = {};
    
    fdivs = jq('form[name="search"] div.field')
    fdivs.each(function(n, el) {
	el = jq(el);
	fid = 'hh_' + n;
	el.attr('id', fid);
	checkid = 'hhc_' + n;
	jq(el.find('label')[0]).attr('for', checkid);
	el.children().each(function(n, ch) {
	    if (n >= 2) {
		if (!HalfwayHouse.options[fid]) {
		    HalfwayHouse.options[fid] = new Array();
		}
		HalfwayHouse.options[fid].push(ch);
		jq(ch).remove();
	    } 
	});
	checker = jq('<input type="checkbox" />');
	checker.attr('id', checkid);
	checker.prependTo(el).click(
	    function(foo) {
		container = jq(this).parent('div.field');
		if (jq(this).attr('checked')) {
		    cid = container.attr('id');
		    bits = HalfwayHouse.options[cid];
		    for (i=0; i<bits.length; i++) {
			container.append(bits[i]);
		    }
		}
		else {
		    container.children().each(function(x, ch) {
			if (x >= 3) {
			    jq(ch).remove();
			}
		    });
		}
	    });
    });
});


