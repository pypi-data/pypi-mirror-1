event = null;

function refreshForm() {
    var args = {
        '_action_': 'save_console',
        'console': $('output').innerHTML};
    var req = getXMLHttpRequest();
    req.open('POST', './');
    req.setRequestHeader('content-type', 'application/x-www-form-urlencoded')
    var d = sendXMLHttpRequest(req, queryString(args));
    d.addCallbacks(finishRefreshForm, errorResponse);
    $('refresh-button').innerHTML = 'refreshing...';
    $('refresh-button').disabled = true;
}

function finishRefreshForm(res) {
    document.location.href = location.href;
    $('refresh-button').innerHTML = 'refreshed';
    $('refresh-button').style.color = '#090';
    setTimeout(function () {
        $('refresh-button').innerHTML = 'refresh';
        $('refresh-button').style.color = '#000';
        $('refresh-button').disabled = false;
    }, 2000);
}

function submitForm() {
    try {
        sendInputCommand();
    } catch (e) {
        writeError('Error in sendCommand: ' + e);
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
    var output = [];
    for (var i=0; i<lines.length; i++) {
        if (i) {
            var prompt = '...';
        } else {
            var prompt = '>>>';
        }
        output.push(SPAN({'class': 'prompt'}, prompt));
        output.push(' '+lines[i]);
        if (i == lines.length-1) {
            output.push(SPAN({'id': 'pending-command'}, '...'));
        }
        output.push(BR());
    }
    output = SPAN({'class': 'input'}, output);
    writeMessage(output);
    var args = {
        '_action_': 'run',
        '_': 'true',
        'command': command};
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

function addResponse(res) {
    removePending();
    try {
        var result = evalJSONRequest(res);
    } catch (e) {
        writeError('Bad JSON response: '+res.responseText);
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
        var el = domHTML(SPAN({'class': 'output'}),
                         escapeWhitespace(text));
        writeMessage(el, true);
    }
    if (result['result_html']) {
        var el = domHTML(SPAN({'class': 'output'}),
                         result['result_html']);
        writeMessage(el, false);
    }
    if (result['result_javascript']) {
        try {
            eval(result['result_javascript']);
        } catch (e) {
            writeError('Error evaluating "'
                       + result['result_javascript']
                       + '": ' + e);
        }
    }
    for (name in result['changed']) {
        createObject(name, result['changed'][name]);
    }
    for (var i=0; i<result['removed'].length; i++) {
        removeObject(name, result['removed'][i]);
    }
    $('input').focus();
    if ($('input').autoSubmit) {
        expandInput();
    }
}

function createObject(name, html) {
    removeObject(name);
    var td = TD({'class': 'py-value'});
    td.innerHTML = html;
    var newDiv = TR(
      {id: 'object-'+name, 'class': 'py-object'},
      TD({'class': 'py-name'}, name+'='),
      td);
    $('objects').appendChild(newDiv);
}

function removeObject(name) {
    existing = $('object-'+name);
    if (existing) {
        removeElement(existing);
    }
}

function errorResponse(error) {
    removePending();
    var result = error.req.responseText;
    writeError(result);
}

function removePending() {
    var p = $('pending-command');
    if (p !== null) {
        removeElement(p);
    }
}

function writeError(msg) {
    el = SPAN({'class': 'error'}, msg);
    writeMessage(el, true);
}

function domHTML(el, content) {
    el.innerHTML = content;
    return el;
}

function escapeWhitespace(content) {
    /* like escapeHTML, but also preserves whitespace */
    content = escapeHTML(content);
    content = content.replace(/\n/, '<br>\n');
    /* This isn't really very good: */
    content = content.replace(/  /, ' &nbsp;');
    return content;
}

function writeMessage(el, br) {
    var div = $('output');
    div.appendChild(el);
    if (br) {
        div.appendChild(BR());
    }
}

function writeMessages(els, br) {
    for (var i=0; i<els.length; i++) {
        writeMessage(els[i], br);
    }
}

function clearOutput() {
    var div = $('output');
    replaceChildNodes(div);
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
        var newEl = TEXTAREA(stdops);
        var text = '-';
        var title = 'Reduce size of input (or use Insert)';
    } else {
        stdops['type'] = 'text';
        stdops['autocomplete'] = 'off';
        var newEl = INPUT(stdops);
        var text = '+';
        var title = 'Expand size of input (or use Insert)';
    }
    newEl.value = input.value;
    newEl.id = input.id;
    swapDOM(input, newEl);
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
    var oldHTML = container.innerHTML;
    var name = getText($(containerId+'-name'));
    var args = getText($(containerId+'-args'));
    var body = getText($(containerId+'-body'));
    var bodyLines = body.split(/\n/).length;
    var newForm = (
        '<div>\n'
        + '<input type="hidden" name="name" value="'
        + escapeHTML(name) + '">'
        + '<code>def <b>'+name+'</b>(</code>'
        + '<input type="text" name="args" value="'
        + escapeHTML(args) + '" style="width: 50%">'
        + '<code>)</code><br>\n'
        + '&nbsp; <textarea name="body" style="width: 90%"'
        + ' wrap="off" rows="' + bodyLines + '">'
        + escapeHTML(body) + '</textarea><br>\n'
        + '<button onclick="return submitFunc(\''
        + containerId + '\', \'' + action
        + '\')">save</button>\n'
        + '<button onclick="return cancelFunc(\''
        + containerId + '\')">cancel</button>'
        + '</div>\n');
    container.innerHTML = newForm;
    container.oldHTML = oldHTML;
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
            var pre = PRE({id: errorId});
            pre.innerHTML = escapeHTML(result['error']);
            $(containerId).appendChild(pre);
        }
    }, errorResponse);
    return false;
}

function cancelFunc(containerId) {
    var container = $(containerId);
    var oldHTML = container.oldHTML;
    container.innerHTML = oldHTML;
    container.oldHTML = null;
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
