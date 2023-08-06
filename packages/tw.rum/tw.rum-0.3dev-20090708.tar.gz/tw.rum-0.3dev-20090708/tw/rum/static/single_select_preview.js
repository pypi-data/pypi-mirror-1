dojo.addOnLoad(function()
{
    dojo.query("a.rum-single-select-preview").connect("onclick",function(e){
        e.preventDefault();
        var preview_base = dojo.attr(e.target,"href");
        var parent = e.target.parentNode;
        var options = dojo.query('option', parent);
        for (var i=0;i<options.length;i++){
            if (options[i].selected){
                var selected=options[i];
                var key=dojo.attr(selected,"value");
                var full_url=preview_base+"/"+ key;
                window.open(full_url);
                return;
            }
        }
        
    });
});
