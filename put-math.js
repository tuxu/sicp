#!/usr/bin/env phantomjs

// Usage: ./put-math.js json_db file1 [file2 ...]
//  json_db: existing JSON file that contains the SVG database;
//  file1, file2, ...: the output files to modify.

// This replaces all the LaTeX markup in given output files with SVG. 
// It does it by searching for LaTeX strings delimited by \( \) or \[ \] 
// and looks up the mapping from LaTeX to SVG in the JSON database.

// (c) 2017 Tino Wagner (adaptation to SVG)
// (c) 2014 Andres Raba, GNU GPL v.3.

var system = require('system'),
    fs = require('fs');

phantom.injectJs('lib/md5.js');

// LaTeX is enclosed in \( \) or \[ \] delimiters,
// first pair for inline, second for display math:
var pattern = /\\\([\s\S]+?\\\)|\\\[[\s\S]+?\\\]/g;

if (system.args.length <= 2) {
  console.log("Usage: ./put-math.js json_db file1 [file2 ...]");
  phantom.exit();
} 
else {
  var db = system.args[1];          // JSON database
  var args = system.args.slice(2);  // file1, file2, ...
  try {
    var mathml = JSON.parse(fs.read(db));
  } 
  catch(error) {
    console.log(error);
    phantom.exit();
  }
  args.forEach(function (arg) {
    try {
      var file = fs.read(arg);
      // Replace LaTeX with SVG or paint LaTeX blue
      // if mapping not found in JSON database:
      var file = file.replace(pattern, function (latex) {
        var filename = 'fig/math/' + md5(latex) + '.svg';
        var svgItem = mathml[latex];
        if (!svgItem) {
          return "<span style='color:blue'>" + latex + "</span>";
        }
        var svgCode = "";
        if (svgItem.code.substr(0, 5) != '<?xml') {
          svgCode += '<?xml version="1.0" encoding="utf-8"?>\n';
        }
        svgCode += svgItem.code;
        fs.write(filename, svgCode, 'w');
        var elem = document.createElement('img');
        elem.setAttribute('src', filename);
        var imgClass = 'math-inline';
        if (latex.substr(0, 2) == '\\[') {
          imgClass = 'math-display';
        }
        elem.setAttribute('class', imgClass);
        elem.setAttribute('style', svgItem.style);
        elem.setAttribute('alt', latex.replace('\n', '&#10;'));
        return elem.outerHTML.replace(/\/?>$/, '/>');
      });
      fs.write(arg, file, 'w');
    }
    catch(error) {
      console.log(error);
    }
  });
  phantom.exit();
}
