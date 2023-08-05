function getargs(form) {
    var list = {};
    for (var i=1; i<arguments.length; i++) {
        val = form[arguments[i]]
        if (val) {
            list[arguments[i]] = val.value;
        }
    }
    return list;
}