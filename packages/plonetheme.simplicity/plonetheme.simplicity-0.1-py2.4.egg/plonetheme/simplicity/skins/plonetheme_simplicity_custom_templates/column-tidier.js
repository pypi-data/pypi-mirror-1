window.onload = function() {
    if (!document.getElementById("portal-column-two") && (document.getElementById("portal-column-content"))) {
        pcc = document.getElementById("portal-column-content");
        if (document.getElementById("login-form")) { lg = document.getElementById("login-form");}
        pcc.style.borderRight="0px !important;";
        try { lg.style.marginLeft="0"; }
		catch(err) {
			// don't bother
		}
    }
    
    // on earlier versions of Plone 3, convert three letter day of week names to two letters
    
    table_rows = document.getElementsByTagName("tr");
    for (i=0; i<table_rows.length; i++) {
        if (table_rows[i].className=='weekdays') {
            table_heads = table_rows[i].getElementsByTagName("th");
            for (j=0; j<table_heads.length; j++) {
               
                if (table_heads[j].innerHTML.length==3) {
                    var inner = table_heads[j].innerHTML;
                                 
                    table_heads[j].innerHTML = inner.substr(0,2);
                    
                }
            }
        }
    }
}
