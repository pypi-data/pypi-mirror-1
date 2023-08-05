function doctest(verbosity) {
  var output = $('doctestOutput');
  var reporter = new Reporter(output, verbosity||0);
  map(function (el) {runDoctest(el, reporter)}, 
      getElementsByTagAndClassName('pre', 'doctest'));
  reporter.finish();
}

function runDoctest(el, reporter) {
  logDebug('Testing element '+repr(el));
  reporter.startElement(el);
  var parsed = new Parser(el);
  var runner = new JSRunner(reporter)
  for (var i=0; i<parsed.examples.length; i++) {
    runner.run(parsed.examples[i]);
  }
}

function Parser(el) {
  if (this === window) {
    throw('you forgot new!');
  }
  var text = getText(el);
  var lines = text.split(/\n/);
  this.examples = [];
  var example_lines = [];
  var output_lines = [];
  for (var i=0; i<lines.length; i++) {
    var line = lines[i];
    if (/^[$]/.test(line)) {
      if (example_lines.length) {
        ex = new Example(example_lines, output_lines);
        this.examples.push(ex);
      }
      example_lines = [];
      output_lines = [];
      line = strip(line.substr(1));
      example_lines.push(line);
    } else if (/^>/.test(line)) {
      if (! example_lines.length) {
        throw('Bad example: '+repr(line)+'\n'
              +'> line not preceded by $');
      }
      line = strip(line.substr(1));
      example_lines.push(line);
    } else {
      output_lines.push(line);
    }
  }
  if (example_lines.length) {
    ex = new Example(example_lines, output_lines);
    this.examples.push(ex);
  }
}

function Example(example, output) {
  if (this === window) {
    throw('you forgot new!');
  }
  this.example = example.join('\n');
  this.output = output.join('\n');
}  

function Reporter(container, verbosity) {
  if (this === window) {
    throw('you forgot new!');
  }
  if (! container) {
    throw('No container passed to Reporter');
  }
  this.container = container;
  this.verbosity = verbosity;
  this.success = 0;
  this.failure = 0;
  this.elements = 0;
}

Reporter.prototype.startElement = function (el) {
  this.elements += 1;
}

Reporter.prototype.reportSuccess = function (example, output) {
  if (this.verbosity > 0) {
    if (this.verbosity > 1) {
      this.write('Trying:\n');
      this.write(this.formatOutput(example.example));
      this.write('Expecting:\n');
      this.write(this.formatOutput(example.output));
      this.write('ok\n');
    } else {
      this.writeln(example.example + ' ... passed!');
    }
  }
  this.success += 1;
}

Reporter.prototype.reportFailure = function (example, output) {
  this.write('Failed example:\n');
  this.write('<span style="color: #00f">'
             +this.formatOutput(example.example)
             +'</span>');
  this.write('Expected:\n');
  this.write(this.formatOutput(example.output));
  this.write('Got:\n');
  this.write(this.formatOutput(output));
  this.failure += 1;
}

Reporter.prototype.finish = function () {
  this.writeln((this.success+this.failure)
               + ' tests in ' + this.elements + ' items.');
  if (this.failure) {
    var color = '#f00';
  } else {
    var color = '#0f0';
  }
  this.writeln(this.success + ' passed and '
               + '<span style="color: '+color+'">'
               + this.failure + '</span> failed.');
}

Reporter.prototype.writeln = function (text) {
  this.write(text+'\n');
}

Reporter.prototype.write = function (text) {
  var leading = /^[ ]*/.exec(text)[0];
  text = text.substr(leading.length);
  for (var i=0; i<leading.length; i++) {
    text = String.fromCharCode(160)+text;
  }
  text = text.replace(/\n/g, '<br>');
  this.container.innerHTML += text;
}

Reporter.prototype.formatOutput = function (text) {
  if (! text) {
    return '    <span style="color: #999">(nothing)</span>\n';
  }
  var lines = text.split(/\n/);
  var output = ''
  for (var i=0; i<lines.length; i++) {
    output += '    '+escapeHTML(lines[i])+'\n';
  }
  return output;
}

function JSRunner(reporter) {
  if (this === window) {
    throw('you forgot new!');
  }
  this.reporter = reporter;
}

JSRunner.prototype.run = function (example) {
  var cap = new OutputCapturer();
  cap.capture();
  try {
    var result = window.eval(example.example);
  } catch (e) {
    result = 'Error: ' + e;
  }
  if (typeof result != 'undefined'
      && result !== null) {
    writeln(repr(result));
  }
  cap.stopCapture();
  success = this.checkResult(cap.output, example.output)
  if (success) {
    this.reporter.reportSuccess(example, cap.output);
  } else {
    this.reporter.reportFailure(example, cap.output);
    logDebug('Failure: '+repr(example.output)
             +' != '+repr(cap.output));
  }
}

JSRunner.prototype.checkResult = function (got, expected) {
  if (! /\n$/.test(expected)) {
    expected += '\n'
  }
  if (! /\n$/.test(got)) {
    got += '\n'
  }
  return got == expected;
}

function OutputCapturer() {
  if (this === window) {
    throw('you forgot new!');
  }
  this.output = '';
}

var output = null;

OutputCapturer.prototype.capture = function () {
  output = this;
}

OutputCapturer.prototype.stopCapture = function () {
  output = null;
}

OutputCapturer.prototype.write = function (text) {
  this.output += text;
}

function writeln() {
  for (var i=0; i<arguments.length; i++) {
    write(arguments[i]);
    if (i) {
      write(' ');
    }
  }
  write('\n');
}

function write(text) {
  if (output !== null) {
    output.write(text);
  } else {
    log(text);
  }
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
