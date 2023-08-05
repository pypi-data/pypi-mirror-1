outputHTML = ''
event = null;

function submitForm() {
    try {
        sendInputCommand();
    } catch (e) {
        outputHTML += '<br>\n<span class="error">'
        + 'Error in sendCommand: '
        + e + '</span><br>\n';
        refreshDisplay();
    }
    return false;
}

function sendInputCommand() {
    var command = getCommand();
    if (command == '') {
        $('input').focus();
        return false;
    }
    var form = $('input_form');
    if (! form.history) {
        form.history = [];
    }
    form.history.push(command);
    clearCommands();
    sendCommand(command);
}

function sendCommand(command) {
    var lines = command.split(/\n/);
    outputHTML = '<span class="input"><span class="prompt">&gt;&gt;&gt;</span> ';
    outputHTML += lines[0];
    for (var i=1; i<lines.length; i++) {
        outputHTML += '\n<span class="prompt">...</span> ' + lines[i];
    }
    outputHTML += '</span>\n';
    var args = {
        '_action_': 'run',
        '_': 'true',
        'command': command}
    var d = doSimpleXMLHttpRequest('./', args);
    d.addCallbacks(addResponse, errorResponse);
}

function getCommand() {
    var command = $('input');
    return rstrip(command.value);
}

function clearCommands() {
    $('input').value = '';
}

function doCallback(uri, insertInto, args) {
    var req = getXMLHttpRequest();
    req.open('POST', uri);
    args = serializeJSON(args);
    var d = sendXMLHttpRequest(req, args);
    d.addCallbacks(function (res) {
        var text = res.responseText;
        $(insertInto).innerHTML = text;
    }, errorResponse);
    return false;
}

function serializeJSON(obj) {
    var t = typeof obj;
    if (t == 'number') {
        return t;
    } else if (t == 'boolean') {
        if (obj) {
            return 'true';
        } else {
            return 'false';
        }
    } else if (t == 'string') {
        return repr(obj);
    } else if (obj === null) {
        return 'null';
    } else if (typeof obj.length == 'number') {
        var parts = '[';
        var first = true;
        for (var i=0; i<obj.length; i++) {
            if (! first) {
                parts += ', ';
                first = false;
            }
            parts += serializeJSON(obj[i]);
        }
        return parts + ']';
    } else {
        var parts = '{';
        var first = true;
        for (var i in obj) {
            if (! first) {
                parts += ', ';
                first = false;
            }
            parts += repr(i) + ': ';
            parts += serializeJSON(obj[i]);
        }
        return parts + '}';
    }
}

function addResponse(res) {
    try {
        var result = evalJSONRequest(res);
    } catch (e) {
        outputHTML += '<span class="error">Bad JSON response:\n'
            + escapeHTML(res.responseText) + '</span>';
        refreshDisplay();
        return;
    }
    if (result['clear_screen']) {
        clearOutput();
    }
    var text = result['result'];
    if (text) {
        text = rstrip(text)+'\n';
    }
    if (text != null) {
        outputHTML += '<span class="output">'
            + escapeHTML(text) + '</span>';
    }
    if (result['result_html']) {
        outputHTML += result['result_html'];
    }
    if (result['result_javascript']) {
        try {
            eval(result['result_javascript']);
        } catch (e) {
            outputHTML += '<span class="error">'
                + 'Error evaluating '
                + escapeHTML(result['result_javascript'])
                + ':\n' + escapeHTML(e)
                + '</span>';
        }
    }
    for (name in result['changed']) {
        createObject(name, result['changed'][name]);
    }
    for (var i=0; i<result['removed'].length; i++) {
        removeObject(name, result['removed'][i]);
    }
    refreshDisplay();
    $('input').focus();
    if ($('input').autoSubmit) {
        expandInput();
    }
}

function createObject(name, html) {
    removeObject(name);
    var td = MochiKit.DOM.TD({'class': 'py-value'});
    td.innerHTML = html;
    var newDiv = MochiKit.DOM.TR(
    {id: 'object-'+name, 'class': 'py-object'},
    MochiKit.DOM.TD({'class': 'py-name'}, name+'='),
    td
    );
    $('objects').appendChild(newDiv);
}

function removeObject(name) {
    existing = $('object-'+name);
    if (existing) {
        removeElement(existing);
    }
}

function errorResponse(error) {
    var result = error.req.responseText;
    outputHTML += '<span class="error">'
        + result + '</span>\n';
    refreshDisplay();
}

function refreshDisplay() {
    var div = $('output');
    div.innerHTML = outputHTML;
}

function clearOutput() {
    outputHTML = '';
    refreshDisplay();
    $('input').focus();
    return false;
}

function expandInputEvent() {
    expandInput();
    return false;
}

function expandInput() {
    var link = $('expand_input');
    var input = $('input_form').elements.input;
    stdops = {
        name: 'input',
        style: 'width: 100%',
        autocomplete: 'off',
        'class': 'command-input',
        onkeypress: upArrow
    };
    if (input.tagName == 'INPUT') {
        stdops['rows'] = '5';
        var newEl = MochiKit.DOM.TEXTAREA(stdops);
        var text = '-';
        var title = 'Reduce size of input (or use Insert)';
    } else {
        stdops['type'] = 'text';
        stdops['autocomplete'] = 'off';
        var newEl = MochiKit.DOM.INPUT(stdops);
        var text = '+';
        var title = 'Expand size of input (or use Insert)';
    }
    newEl.value = input.value;
    newEl.id = input.id;
    MochiKit.DOM.swapDOM(input, newEl);
    newEl.focus();
    link.innerHTML = text;
    link.setAttribute('title', title);
    return newEl;
}

function upArrow(event) {
    input = $('input_form').elements.input;
    if (window.event) {
        event = window.event;
    }
    if (event.keyCode == 45) {
        // Insert key
        expandInput();
        return false;
    }
    if (event.keyCode == 13 &&
        (event.shiftKey || event.ctrlKey)) {
        // Shift+Enter or Ctrl+Enter
        if (input.nodeName == 'INPUT') {
            // Expand...
            input = expandInput();
            input.autoSubmit = true;
            if (input.value) {
                insertAtCursor(input, '\n');
            }
        } else {
            // Insert newline...
            insertAtCursor(input, '\n');
        }
        return false;
    }
    if (event.keyCode == 13 && input.autoSubmit) {
        input.form.onsubmit();
        return false;
    }
    if (event.keyCode != 38 && event.keyCode != 40) {
        // not an up- or down-arrow
        return true;
    }
    if (input.nodeName == 'TEXTAREA') {
        // no history in textarea
        return true;
    }
    var dir = event.keyCode == 38 ? 1 : -1;
    var history = input.form.history;
    if (! history) {
        history = input.form.history = [];
    }
    var pos = input.historyPosition || 0;
    if (! pos && dir == -1) {
        return true;
    }
    if (! pos && input.value) {
        history.push(input.value);
        pos = 1;
    }
    pos += dir;
    if (history.length-pos < 0) {
        pos = 1;
    }
    if (history.length-pos > history.length-1) {
        input.value = '';
        return true;
    }
    input.historyPosition = pos;
    var line = history[history.length-pos];
    input.value = line;
}

function editFunc(containerId, action) {
    var container = $(containerId);
    var name = getText($(containerId+'-name'));
    var args = getText($(containerId+'-args'));
    var body = getText($(containerId+'-body'));
    var newForm = (
        '<div>\n'
        + '<input type="hidden" name="name" value="'
        + escapeHTML(name) + '">'
        + '<code>def <b>'+name+'</b>(</code>'
        + '<input type="text" name="args" value="'
        + escapeHTML(args) + '" style="width: 50%">'
        + '<code>)</code><br>\n'
        + '&nbsp; <textarea name="body" style="width: 90%" rows="5">'
        + escapeHTML(body) + '</textarea><br>\n'
        + '<button onclick="return submitFunc(\''
        + containerId + '\', \'' + action
        + '\')">save</button>\n'
        + '</div>\n');
    container.innerHTML = newForm;
}

function submitFunc(containerId, action) {
    var container = $(containerId);
    var fields = formContents(container);
    fields = queryString(fields[0], fields[1]);
    var req = getXMLHttpRequest();
    req.open('POST', action);
    req.setRequestHeader('content-type', 'application/x-www-form-urlencoded')
    var d = sendXMLHttpRequest(req, fields);
    d.addCallbacks(function (res) {
        var result = evalJSONRequest(res);
        if (result['result']) {
            $(containerId).innerHTML = result['result'];
        } else {
            errorId = containerId+'-error';
            if ($(errorId)) {
                removeElement(errorId);
            }
            var pre = MochiKit.DOM.PRE({id: errorId});
            pre.innerHTML = escapeHTML(result['error']);
            $(containerId).appendChild(pre);
        }
    }, errorResponse);
    return false;
}

function getText(el) {
    var text = '';
    for (var i=0; i<el.childNodes.length; i++) {
        var sub = el.childNodes[i];
        if (sub.nodeType == 3) {
            // TEXT_NODE
            text += sub.nodeValue;
        } else if (sub.childNodes) {
            text += getText(sub);
        }
    }
    return text;
}

function expandForm(button) {
    var id = button.getAttribute('id');
    var div = $(id+'-form');
    toggleElementClass('hidden', div);
    if (hasElementClass(div, 'hidden')) {
        // We're just hiding the form...
        button.innerHTML = button.oldHTML;
        return false;
    }
    var field = $(id+'-filename');
    if (field) {
        field.focus();
    }
    button.oldHTML = button.innerHTML;
    button.innerHTML = '&lt;&lt;';
    return false;
}

function submitInteractive(action, buttonId) {
    var container = buttonId+'-form';
    var fields = formContents(container);
    fields = queryString(fields[0], fields[1]);
    var req = getXMLHttpRequest();
    req.open('POST', action);
    req.setRequestHeader('content-type', 'application/x-www-form-urlencoded')
    var d = sendXMLHttpRequest(req, fields);
    d.addCallbacks(function (res) {
        addResponse(res);
        expandForm(buttonId);
    }, errorResponse);
    return false;
}

function insertAtCursor(field, value) {
    if (document.selection) {
        // IE
        field.focus();
        sel = document.selection.createRange();
        sel.text = value;
    } else if (field.selectionStart !== undefined) {
        var start = field.selectionStart;
        var end = field.selectionEnd;
        field.value = field.value.substring(0, start)
            + value
            + field.value.substring(end, field.value.length);
    } else {
        field.value += value;
    }
}
