dojo.addOnLoad(function()
{
    dojo.query("a.span_expander").connect("onclick",function(e){
        e.preventDefault();
        var parent = e.target.parentNode;
        var hidden = dojo.query('.rum-expandable-span-hidden', parent);
        var tohide = dojo.query('.rum-expandable-span-visible', parent);
        tohide.addClass('rum-expandable-span-hidden').removeClass('rum-expandable-span-visible');
        
        hidden.addClass('rum-expandable-span-visible').removeClass('rum-expandable-span-hidden');
    });
});


