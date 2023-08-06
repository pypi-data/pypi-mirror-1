dojo.addOnLoad(function()
{
    dojo.query("a.rum-single-select-preview").connect("onclick",function(e){
        e.preventDefault();
        var preview_base = dojo.attr(e.target,"href");
        var parent = e.target.parentNode;
        var selected = dojo.query('option[selected="selected"]', parent)[0];
        var key=dojo.attr(selected,"value");
        var full_url=preview_base+"/"+ key;
        window.open(full_url);
    });
});
