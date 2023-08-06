function EditPasswordField(params, elem) {
    var elem = dojo.byId(elem);
    var checkbox = document.createElement('input');
    dojo.attr(checkbox, {type:'checkbox', id:this.new_id()});
    dojo.connect(checkbox, 'onchange', function(ev) {
        var checked = dojo.attr(checkbox, 'checked');
        dojo.attr(elem, 'disabled', !checked);
        if (checked) {
            elem.focus();
            elem.select();
        }
    });
    var label = document.createElement('label');
    dojo.attr(label, {
        'for': dojo.attr(checkbox, 'id'),
        style: 'display: inline'
    });
    label.innerHTML = params.checkbox_label;
    label.appendChild(checkbox);
    elem.parentNode.appendChild(label);
}

EditPasswordField.prototype.new_id = (function(value) {
    return function() {
        return 'edit-password-cb-' + (++value);
    }
})(0);
