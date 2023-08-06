function toggleSelect(content, source, nameprefix) {
    var state = source.checked;

    // now:  find other items like the stated one (IN id=content)
    var inputs = getElementsByTagAndClassName('input', null, content);
    for (var i=0; i<inputs.length; i++) {
        var c = inputs[i];
        var n = c.name;
        if (c.type == 'checkbox') {
            if ((n.length >= nameprefix.length) && (nameprefix == n.substring(0,nameprefix.length))) {
                c.checked = state;
            }
        }
    }
}

