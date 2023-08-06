/******************************************************************************
    scripts.js
    Copyright (C) 2008 Feihong Hsu http://feihonghsu.com

    This script is part of StarScream and is released under
    the New BSD License: http://www.opensource.org/licenses/bsd-license.php
******************************************************************************/
    
// var slides is defined in another file
var slideIndex = 0;
var fontSize = 0;      // set this value inside the ready handler

// Change the inner HTML of the #slide DIV. Adjust the font and set the gradient of the header.
function changeContent(index) {
    $("#slide").html(slides[index]);
    setContentFontSize(fontSize);
    setHeaderGradient();    
    return false;
}

// Set the gradient for the slide header. This uses the jquery.gradient plugin. I can't get this to work in IE.
function setHeaderGradient() {
    var headerBgColor = $('#header').css('background-color');
    
    if (headerBgColor != undefined) {
        $('#header').gradient({
            from: getHexFromRgb(headerBgColor),
            to: '333333'
        });
    }
}

// Convert a string of the form "rgb(255, 167, 222)" to a string of the form "ffa7de".
function getHexFromRgb(/* string */ rgb) {
    if (rgb.charAt(0) == "#")
        return rgb.substr(1, rgb.length-1);
        
    var v = /rgb\((\d+), (\d+), (\d+)\)/.exec(rgb);
    
    // Function that converts an integer string (with value < 255) to a hex string
    var convert = function(s) {
        var i = parseInt(s);
        var d1 = parseInt(i / 16);
        var d2 = parseInt(i - d1*16);
        d1 = d1 > 9 ? String.fromCharCode(d1 + 87) : d1;
        d2 = d2 > 9 ? String.fromCharCode(d2 + 87) : d2;
        return d1.toString() + d2.toString();
    };
    
    v = $.map([v[1], v[2], v[3]], convert);
    return v.join(""); 
}

// Advances to the next slide, changing the content
function next() {
    if (slideIndex < slides.length-1) {
        slideIndex++;
        changeContent(slideIndex);
    }  
}

// Jumps to the previous slide, changing the content
function prev() {
    if (slideIndex > 0) {
        slideIndex--;
        changeContent(slideIndex);
    }
}

// Adjusts the font by by the specified number of pixels
function textZoom(/* int */ offset) {
    fontSize += offset;
    setContentFontSize(fontSize);
}

// Sets the font-size CSS style of the #content DIV
function setContentFontSize(/* int */ fontSize) {
    var fontSizeStr = fontSize.toString() + "px";
    $("#content").css("font-size", fontSizeStr);        
}

// Document ready handler
$(document).ready(function(e) {
    // Get the initial font-size CSS style
    fontSize = $("body").css("font-size");
    fontSize = parseInt(fontSize.substr(0, fontSize.length-2)); 
    
    changeContent(0);

    // Handle key presses:
    $(document).keypress(function(e) {
        var keyChar = String.fromCharCode(e.which);
        
        switch (keyChar) {
            case 'k':
                prev();
                break;
            case 'j':
                next();
                break;
            case '-':
                textZoom(-1);
                break;
            case '=':
            case '+':
                textZoom(1);
                break;
        }        
    });
});