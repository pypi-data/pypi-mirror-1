function update_preview(name, color)
{
    document.getElementById(name).style.backgroundColor = color;
}

function rgbStringToHex(rgbString)
{
    // Ripped off from http://www.linuxtopia.org/online_books/javascript_guides/javascript_faq/rgbtohex.htm
    function numToHex(n)
    {
         if (n == null) return "00";
         n = parseInt(n);
         if (n == 0 || isNaN(n)) return "00";
         n = Math.max(0, n); n = Math.min(n, 255); n = Math.round(n);
         return "0123456789ABCDEF".charAt((n - n % 16) / 16)
              + "0123456789ABCDEF".charAt(n % 16);
    }
    
    var hexString = "";
    var numericStrings = rgbString.slice(4, -1).split(', ');
    var curNumericString;
    while (curNumericString = numericStrings.shift())  // rgb(1, 2, 3) --> ["1", "2", "3"]
        hexString += numToHex(parseInt(curNumericString));
    return hexString;
}

// Return the hex color (e.g. "F0EFD7") displayed in the swatch for the given CSS property.
function get_picker_color(cssProperty) {
    return rgbStringToHex(document.getElementById(cssProperty + '_pre').style.backgroundColor);
}

var fontStart = document.css_edit_form.fontFamily.value;
var headingFontStart = document.css_edit_form.headingFontFamily.value;
var borderStyleStart = document.css_edit_form.borderStyle.value;
var borderStyleAnnStart = document.css_edit_form.borderStyleAnnotations.value;
var textTransformStart = document.css_edit_form.textTransform.value;

function fontChanged(fieldname, formname) {  
       document.css_edit_form[fieldname].value = document[formname].component.value;
    }
    
function cancelFont(div, fieldname, resetValue) {
	    document.css_edit_form[fieldname].value = [resetValue];
	    document.getElementById(div).style.display = 'none';
	}

function get_picker_font() {
    var str=document.css_edit_form.fontFamily.value;
    str = str.replace(/"/g,"'");
    return str;
}

function displayDiv(div, where) {
	document.getElementById(div).style.display = 'block';
	document.getElementById(div).style.position = 'absolute';
	document.getElementById(div).style.left = findPos(where)[0]+'px';	
	document.getElementById(div).style.top = findPos(where)[1]-1+'px';
}

function hideDiv(div) {
	document.getElementById(div).style.display = 'none';	
}

function findPos(obj) {
	obj=document.getElementById(obj);
	var curleft = curtop = 0;
	if (obj.offsetParent) {
		curleft = obj.offsetLeft
		curtop = obj.offsetTop
		while (obj = obj.offsetParent) {
			curleft += obj.offsetLeft
			curtop += obj.offsetTop
		}
	}
	
	return [curleft, curtop];
}