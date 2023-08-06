import unittest
import jsmin
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

class JsTests(unittest.TestCase):
    def _minify(self, js):
        out = StringIO()
        jsmin.JavascriptMinify().minify(StringIO(js), out)
        return out.getvalue()

    def assertEqual(self, thing1, thing2):
        if thing1 != thing2:
            print((repr(thing1)))
            print((repr(thing2)))
            raise AssertionError
        return True
    
    def testQuoted(self):
        js = r'''
        Object.extend(String, {
          interpret: function(value) {
            return value == null ? '' : String(value);
          },
          specialChar: {
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '\\': '\\\\'
          }
        });

        '''
        expected = r"""Object.extend(String,{interpret:function(value){return value==null?'':String(value);},specialChar:{'\b':'\\b','\t':'\\t','\n':'\\n','\f':'\\f','\r':'\\r','\\':'\\\\'}});"""
        self.assertEqual(self._minify(js), expected)

    def testSingleComment(self):
        js = r'''// use native browser JS 1.6 implementation if available
        if (Object.isFunction(Array.prototype.forEach))
          Array.prototype._each = Array.prototype.forEach;

        if (!Array.prototype.indexOf) Array.prototype.indexOf = function(item, i) {

        // hey there
        function() {// testing comment
        foo;
        //something something

        location = 'http://foo.com;';   // goodbye
        }
        //bye
        '''
        expected = r""" 
if(Object.isFunction(Array.prototype.forEach))
Array.prototype._each=Array.prototype.forEach;if(!Array.prototype.indexOf)Array.prototype.indexOf=function(item,i){ function(){ foo; location='http://foo.com;';}"""
        # print expected
        self.assertEqual(self._minify(js), expected)

    def testMultiComment(self):
        js = r"""
        function foo() {
            print('hey');
        }
        /*
        if(this.options.zindex) {
          this.originalZ = parseInt(Element.getStyle(this.element,'z-index') || 0);
          this.element.style.zIndex = this.options.zindex;
        }
        */
        another thing;
        """
        expected = r"""function foo(){print('hey');}
another thing;"""
        self.assertEqual(self._minify(js), expected)

    def testRe(self):
        js = r'''  
        var str = this.replace(/\\./g, '@').replace(/"[^"\\\n\r]*"/g, '');
        return (/^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]*$/).test(str);
        });'''
        expected = r"""var str=this.replace(/\\./g,'@').replace(/"[^"\\\n\r]*"/g,'');return(/^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]*$/).test(str);});"""
        self.assertEqual(self._minify(js), expected)

    def testIgnoreComment(self):
        js = r"""
        var options_for_droppable = {
          overlap:     options.overlap,
          containment: options.containment,
          tree:        options.tree,
          hoverclass:  options.hoverclass,
          onHover:     Sortable.onHover
        }

        var options_for_tree = {
          onHover:      Sortable.onEmptyHover,
          overlap:      options.overlap,
          containment:  options.containment,
          hoverclass:   options.hoverclass
        }

        // fix for gecko engine
        Element.cleanWhitespace(element); 
        """
        expected = r"""var options_for_droppable={overlap:options.overlap,containment:options.containment,tree:options.tree,hoverclass:options.hoverclass,onHover:Sortable.onHover}
var options_for_tree={onHover:Sortable.onEmptyHover,overlap:options.overlap,containment:options.containment,hoverclass:options.hoverclass} 
Element.cleanWhitespace(element);"""
        self.assertEqual(self._minify(js), expected)

    def testHairyRe(self):
        js = r"""
        inspect: function(useDoubleQuotes) {
          var escapedString = this.gsub(/[\x00-\x1f\\]/, function(match) {
            var character = String.specialChar[match[0]];
            return character ? character : '\\u00' + match[0].charCodeAt().toPaddedString(2, 16);
          });
          if (useDoubleQuotes) return '"' + escapedString.replace(/"/g, '\\"') + '"';
          return "'" + escapedString.replace(/'/g, '\\\'') + "'";
        },

        toJSON: function() {
          return this.inspect(true);
        },

        unfilterJSON: function(filter) {
          return this.sub(filter || Prototype.JSONFilter, '#{1}');
        },
        """
        expected = r"""inspect:function(useDoubleQuotes){var escapedString=this.gsub(/[\x00-\x1f\\]/,function(match){var character=String.specialChar[match[0]];return character?character:'\\u00'+match[0].charCodeAt().toPaddedString(2,16);});if(useDoubleQuotes)return'"'+escapedString.replace(/"/g,'\\"')+'"';return"'"+escapedString.replace(/'/g,'\\\'')+"'";},toJSON:function(){return this.inspect(true);},unfilterJSON:function(filter){return this.sub(filter||Prototype.JSONFilter,'#{1}');},"""
        self.assertEqual(self._minify(js), expected)

    def testNoBracesWithComment(self):
        js = r"""
        onSuccess: function(transport) {
            var js = transport.responseText.strip();
            if (!/^\[.*\]$/.test(js)) // TODO: improve sanity check
              throw 'Server returned an invalid collection representation.';
            this._collection = eval(js);
            this.checkForExternalText();
          }.bind(this),
          onFailure: this.onFailure
        });
        """
        expected = r"""onSuccess:function(transport){var js=transport.responseText.strip();if(!/^\[.*\]$/.test(js)) 
throw'Server returned an invalid collection representation.';this._collection=eval(js);this.checkForExternalText();}.bind(this),onFailure:this.onFailure});"""
        self.assertEqual(self._minify(js), expected)
    
    def testSpaceInRe(self):
        js = r"""
        num = num.replace(/ /g,'');
        """
        self.assertEqual(self._minify(js), "num=num.replace(/ /g,'');")
    
    def testEmptyString(self):
        js = r'''
        function foo('') {
        
        }
        '''
        self.assertEqual(self._minify(js), "function foo(''){}")
    
    def testDoubleSpace(self):
        js = r'''
var  foo    =  "hey";
        '''
        self.assertEqual(self._minify(js), 'var foo="hey";')
        
        
if __name__ == '__main__':
    unittest.main()