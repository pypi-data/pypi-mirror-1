TinyMCE_Cleanup.prototype._arrayToRePATCHED = function(a, op, be, md, af) {
  var i, r;
  op = typeof(op) == "undefined" ? "gi" : op;
  r = be;
  for (i = 0; i < a.length; i++) {
    r += this._wildcardToRe(a[i]) + (i != a.length-1 ? "|" : "");
  }
  r += md;
  for (i = 0; i < a.length; i++) {
    r += this._wildcardToRe(a[i]) + (i != a.length-1 ? "|" : "");
  }
  r += af;
  return new RegExp(r, op);
};
TinyMCE_Cleanup.prototype.formatHTML = function (h) {
  var s = this.settings, p = '', i = 0, li = 0, o = '', l;
  h = h.replace(/\r/g,'');
  h = '\n' + h;
  h = h.replace(new RegExp('\\n\\s+', 'gi'), '\n'); // Remove previous formatting
  h = h.replace(this.nlBeforeRe, '\n<$1$2>');
  h = h.replace(this.nlAfterRe, '<$1$2>\n');
  h = h.replace(this.nlBeforeAfterRe, '\n<$1$2$3>\n');
  h += '\n';
  while ((i = h.indexOf('\n', i + 1)) != -1) {
    if ((l = h.substring(li + 1, i)).length != 0) {
      if (this.ouRe.test(l) && p.length >= s.indent_levels) {
        p = p.substring(s.indent_levels);
      }
      if (this.closedRe.test(l)) {
        o += p + '  ' + l + '\n';
      }
      else {
        o += p + l + '\n';
      }
      if (this.inRe.test(l)) {
        p += this.inStr;
      } 
    }
    li = i;
  }
  return o;
};