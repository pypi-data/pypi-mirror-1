var JSRepeater = new Class({
    initialize: function(config) {
        this._first_id = config.first_id;
        this._first_name = config.first_name;
        this._error_class = config.error_class;
        this._max_repetitions = config.max_repetitions;
        this._max_error_text = config.max_error_text;

        this._add_trigger = $(config.add_link_id);
        this._repeater = this._add_trigger.parentNode;
        this._n_repetitions = $ES('.repetition_container', this._repeater).length;
        this._template = this._createTemplate(config.clear_on_init);
        this._add_trigger.addEvent('click', this.onAdd.bind(this));
        this._bindDelHandler(this._repeater);
    },
    onAdd: function(ev) {
        new Event(ev).stop();
        var repetitions = $ES('.repetition_container', this._repeater);
        var nextN = 0;
        if (repetitions.length) {
            if (this._n_repetitions >= this._max_repetitions) {
                alert(this._max_error_text);
                return;
            }
            nextN = this._findN(repetitions[repetitions.length-1]) + 1;
        }
        ++this._n_repetitions;
        var newElem = this._createNewRepetition(nextN);
        this._repeater.insertBefore(newElem, this._add_trigger);
        this._resetRepetition(newElem);
        this._focus(newElem);
    },
    onRemove: function(ev) {
        var evnt = new Event(ev);
        evnt.stop();
        var node = evnt.target;
        while (node.getAttribute('class') != 'repetition_container') {
            node = node.parentNode;
        }
        this._delRepetition(node);
    },
    _delRepetition: function(elem) {
        elem.setStyle('display', 'none');
        var inputs = elem.getElements('*[name]');
        for (var i=0; i<inputs.length; i++) {
            inputs[i].disabled = true;
        }
        --this._n_repetitions;
    },
    _createTemplate: function(remove_from_dom) {
        var el = $ES('.repetition_container', this._repeater)[0];
        var tpl = el.clone();
        if (remove_from_dom) {
            this._delRepetition(el);
        }
        return tpl;
    },
    _resetRepetition: function(elem) {
        // Clear value and remove error class if any
        elem.getElements('*[name]').each(function(e) {
            e.value = '';
            e.removeClass('has_error');
        });
        // Select first (assume is default) options in each dropdown
        elem.getElements('select').each(function(e) {
            e.selectedIndex = 0;
        });
        // Uncheck checkboxes
        elem.getElements('input[type=checkbox]').each(function(e) {
            e.checked = null;
        });
        // Clear error messages
        elem.getElements('.'+ this._error_class).each(function(e) {
            e.remove();
        });
    },
    _createNewRepetition: function(num) {
        var newElem = this._template.clone();
        this._updateIds(newElem, num);
        this._updateNames(newElem, num);
        this._bindDelHandler(newElem);
        return newElem;
    },
    _bindDelHandler: function(el) {
        var h = this.onRemove.bind(this);
        $ES('.del_repetition_trigger', el).addEvent('click', h);
    },
    _updateIds: function(newElem, n) {
        var id_replacement = this._first_id.slice(0, -1) + n;
        var els = this._elementsStartingWithId(newElem, this._first_id);
        for (var i=0; i<els.length; i++) {
            var el = els[i];
            el.id = el.id.replace(this._first_id, id_replacement);
        }
    },
    _updateNames: function(newElem, n) {
        var name_replacement = this._first_name.slice(0, -1) + n;
        var els = this._elementsStartingWithName(newElem, this._first_name);
        for (var i=0; i<els.length; i++) {
            var el = els[i];
            el.name = el.name.replace(this._first_name, name_replacement);
        }
    },
    _focus: function(newElem) {
        var els = newElem.getElements('*[name]');
        for (var i=0; i<els.length; i++) {
            var el = els[i];
            if (el.type == 'hidden') {
                continue;
            }
            try {
                el.focus();
                break;
            } catch (e) {
                alert(e);
                // Damn IE6!
            }
        }
    },
    _elementsStartingWithId: function(source, id) {
        var selector = '*[id^=' + id + ']';
        return source.getElements(selector);
    },
    _elementsStartingWithName: function(source, name) {
        var selector = '*[name^=' + name + ']';
        return source.getElements(selector);
    },
    /*
     * Finds the number of a repeated element.
     */
    _findN: function(repetition)
    {
        var prefix = this._first_id.slice(0,-1);
        var id = this._elementsStartingWithId(repetition, prefix)[0].id;
        var sliced = id.slice(prefix.length);
        var dotPos = sliced.indexOf('.');
        if (dotPos>0) {
            return parseInt(sliced.slice(0,dotPos), 0);
        } else {
            return parseInt(sliced, 0);
        }
    }
});
