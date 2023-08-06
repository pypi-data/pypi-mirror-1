// Helper JS for smartcolorwidget
// Color transformation formulas from easyrgb
// http://www.easyrgb.com/math.php

// Size declarations
/*
 * TODO : Get size from widget at launch for custom skin purpose ?
 */
SLIDER_HEIGHT = 9;
SLIDER_WIDTH = 30;
CURSOR_HEIGHT = 9;
CURSOR_WIDTH = 9;
SLIDER_RANGE = 100;
CURSOR_H_RANGE = 100;
CURSOR_W_RANGE = 100;
s_h_offset = (SLIDER_HEIGHT - 1) / 2;
s_w_offset = (SLIDER_WIDTH - 1) / 2;
c_h_offset = (CURSOR_HEIGHT - 1) / 2;
c_w_offset = (CURSOR_WIDTH - 1) / 2;
var CSS_COLORS = 
{
aliceblue : '#f0f8ff', 	 
antiquewhite : '#faebd7', 	 
aqua : '#00ffff', 	 
aquamarine : '#7fffd4', 	 
azure : '#f0ffff', 	 
beige : '#f5f5dc', 	 
bisque : '#ffe4c4', 	 
black : '#000000', 	 
blanchedalmond : '#ffebcd', 	 
blue : '#0000ff', 	 
blueviolet : '#8a2be2', 	 
brown : '#a52a2a', 	 
burlywood : '#deb887', 	 
cadetblue : '#5f9ea0', 	 
chartreuse : '#7fff00', 	 
chocolate : '#d2691e', 	 
coral : '#ff7f50', 	 
cornflowerblue : '#6495ed', 	 
cornsilk : '#fff8dc', 	 
crimson : '#dc143c', 	 
cyan : '#00ffff', 	 
darkblue : '#00008b', 	 
darkcyan : '#008b8b', 	 
darkgoldenrod : '#b8860b', 	 
darkgray : '#a9a9a9', 	 
darkgrey : '#a9a9a9', 	 
darkgreen : '#006400', 	 
darkkhaki : '#bdb76b', 	 
darkmagenta : '#8b008b', 	 
darkolivegreen : '#556b2f', 	 
darkorange : '#ff8c00', 	 
darkorchid : '#9932cc', 	 
darkred : '#8b0000', 	 
darksalmon : '#e9967a', 	 
darkseagreen : '#8fbc8f', 	 
darkslateblue : '#483d8b', 	 
darkslategray : '#2f4f4f', 	 
darkslategrey : '#2f4f4f', 	 
darkturquoise : '#00ced1', 	 
darkviolet : '#9400d3', 	 
deeppink : '#ff1493', 	 
deepskyblue : '#00bfff', 	 
dimgray : '#696969', 	 
dimgrey : '#696969', 	 
dodgerblue : '#1e90ff', 	 
firebrick : '#b22222', 	 
floralwhite : '#fffaf0', 	 
forestgreen : '#228b22', 	 
fuchsia : '#ff00ff', 	 
gainsboro : '#dcdcdc', 	 
ghostwhite : '#f8f8ff', 	 
gold : '#ffd700', 	 
goldenrod : '#daa520', 	 
gray : '#808080', 	 
grey : '#808080', 	 
green : '#008000', 	 
greenyellow : '#adff2f', 	 
honeydew : '#f0fff0', 	 
hotpink : '#ff69b4', 	 
indianred : '#cd5c5c', 	 
indigo : '#4b0082', 	 
ivory : '#fffff0', 	 
khaki : '#f0e68c', 	 
lavender : '#e6e6fa', 	 
lavenderblush : '#fff0f5', 	 
lawngreen : '#7cfc00', 	 
lemonchiffon : '#fffacd', 	 
lightblue : '#add8e6', 	 
lightcoral : '#f08080', 	 
lightcyan : '#e0ffff', 	 
lightgoldenrodyellow : '#fafad2', 	 
lightgray : '#d3d3d3', 	 
lightgrey : '#d3d3d3', 	 
lightgreen : '#90ee90', 	 
lightpink : '#ffb6c1', 	 
lightsalmon : '#ffa07a', 	 
lightseagreen : '#20b2aa', 	 
lightskyblue : '#87cefa', 	 
lightslategray : '#778899', 	 
lightslategrey : '#778899', 	 
lightsteelblue : '#b0c4de', 	 
lightyellow : '#ffffe0', 	 
lime : '#00ff00', 	 
limegreen : '#32cd32', 	 
linen : '#faf0e6', 	 
magenta : '#ff00ff', 	 
maroon : '#800000', 	 
mediumaquamarine : '#66cdaa', 	 
mediumblue : '#0000cd', 	 
mediumorchid : '#ba55d3', 	 
mediumpurple : '#9370d8', 	 
mediumseagreen : '#3cb371', 	 
mediumslateblue : '#7b68ee', 	 
mediumspringgreen : '#00fa9a', 	 
mediumturquoise : '#48d1cc', 	 
mediumvioletred : '#c71585', 	 
midnightblue : '#191970', 	 
mintcream : '#f5fffa', 	 
mistyrose : '#ffe4e1', 	 
moccasin : '#ffe4b5', 	 
navajowhite : '#ffdead', 	 
navy : '#000080', 	 
oldlace : '#fdf5e6', 	 
olive : '#808000', 	 
olivedrab : '#6b8e23', 	 
orange : '#ffa500', 	 
orangered : '#ff4500', 	 
orchid : '#da70d6', 	 
palegoldenrod : '#eee8aa', 	 
palegreen : '#98fb98', 	 
paleturquoise : '#afeeee', 	 
palevioletred : '#d87093', 	 
papayawhip : '#ffefd5', 	 
peachpuff : '#ffdab9', 	 
peru : '#cd853f', 	 
pink : '#ffc0cb', 	 
plum : '#dda0dd', 	 
powderblue : '#b0e0e6', 	 
purple : '#800080', 	 
red : '#ff0000', 	 
rosybrown : '#bc8f8f', 	 
royalblue : '#4169e1', 	 
saddlebrown : '#8b4513', 	 
salmon : '#fa8072', 	 
sandybrown : '#f4a460', 	 
seagreen : '#2e8b57', 	 
seashell : '#fff5ee', 	 
sienna : '#a0522d', 	 
silver : '#c0c0c0', 	 
skyblue : '#87ceeb', 	 
slateblue : '#6a5acd', 	 
slategray : '#708090', 	 
slategrey : '#708090', 	 
snow : '#fffafa', 	 
springgreen : '#00ff7f', 	 
steelblue : '#4682b4', 	 
tan : '#d2b48c', 	 
teal : '#008080', 	 
thistle : '#d8bfd8', 	 
tomato : '#ff6347', 	 
turquoise : '#40e0d0', 	 
violet : '#ee82ee', 	 
wheat : '#f5deb3', 	 
white : '#ffffff', 	 
whitesmoke : '#f5f5f5', 	 
yellow : '#ffff00', 	 
yellowgreen : '#9acd32'
}

// Regexps declarations
HTML_COLOR_REGEXP = new RegExp("^([#][0-9a-fA-F]{6})$","");
HTML_COLOR_3DIGITS_REGEXP = new RegExp("^([#][0-9a-fA-F]{3})$","");
NO_SHARP_HTML_COLOR_REGEXP = new RegExp("^([0-9a-fA-F]{6})$","");
RGB_COLOR_REGEXP = new RegExp("^([r][g][b][\(][0-9]{1,3}[,]\s*[0-9]{1,3}[,]\s*[0-9]{1,3}[\)])$", "");
RGB_COLORS = new RegExp("^rgb\(\d{1,3},\s*\d{1,3},\s*\d{1,3}\)$","");


// Initialise sliders and cursors position at page launch
/*
 * Should do with widget methods, but much more fun here *grin*
 */
function initDragables(){
	
	jQuery(".color-field").each(function(){
     startColorWidgetFromField(this);
  });	
}

// convert rgb color in hexa color
function rgb2hexa(str) {
   colors=/^rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)$/.exec(str);
   hexa = "#";
   for (i=1; i<colors.length; i++) {
       color = colors[i];
       if (color>255) color=255;
       hexacolor = parseInt(color, 10).toString(16).toLowerCase();
       hexacolor = (hexacolor.length == 1) ? '0' + hexacolor : hexacolor ;
       hexa = hexa + hexacolor;
   }   
   return hexa;
}

// return an hexa html color
function getHexaColor(color) {
    color = color.toLowerCase();
    if (CSS_COLORS[color]) {
        return CSS_COLORS[color];
    }
		else if (HTML_COLOR_REGEXP.test(color)){
			  return color;
		}
		else if (NO_SHARP_HTML_COLOR_REGEXP.test(color)) {
				return  "#" + color;
		}
		else if (HTML_COLOR_3DIGITS_REGEXP.test(color)) {
        return  color + color.substring(1,4);
		}
		else if (RGB_COLOR_REGEXP.test(color)) {
        return  rgb2hexa(color) ;
		}
		else{
				return "#FFFFFF";
		}    
}

// Init the whole edit form from the given color input field
// only if it is possible otherwise do nothing
function startColorWidgetFromField(field) {
    fieldValue = jQuery(field).val();
    if ( fieldValue ) {
        jQuery(field).val(getHexaColor(fieldValue));
        initColorEditFormFromField(field);
    }
}


// Init the whole edit form from the given color input field
function initColorEditFormFromField(field){
	fieldId = getFieldIdFromCurrentNode(field);
	fieldValue = jQuery(field).val();	
	R = parseInt(fieldValue.substring(1,3), 16);
	G = parseInt(fieldValue.substring(3,5), 16);
	B = parseInt(fieldValue.substring(5,7), 16);
	HSL = RGB_to_HSL(R, G, B);
	
	sliderPosition = 100 - (HSL.L + s_h_offset);
	sliderId = "lightness-picker_" + fieldId;
	updateSliderPosition(sliderId, sliderPosition);
	
	selectorXPosition = parseInt((parseInt(HSL.H))/ 3.6) - c_w_offset;
	selectorYPosition = 100 - ( parseInt(HSL.S) + c_h_offset );
	selectorId = "color-selector_" + fieldId;
	updateSelectorPosition(selectorId, selectorXPosition, selectorYPosition);
	
	hueFieldId = "#hue-field_" + fieldId ;
	jQuery(hueFieldId).attr({"value" : HSL.H});
	lightnessFieldId = "#lightness-field_" + fieldId ;
	jQuery(lightnessFieldId).attr({"value" : HSL.L});
	saturationFieldId = "#saturation-field_" + fieldId;
	jQuery(saturationFieldId).attr({"value" : HSL.S});
}


// Helper function to find X pos of an object
function findPosX(obj) {
  var curleft = 0;
  if (obj && obj.offsetParent) {
    while (obj.offsetParent) {
      curleft += obj.offsetLeft;
      obj = obj.offsetParent;
    }
  } else if (obj && obj.x) curleft += obj.x;
  return curleft;
}

// Helper function to find Y pos of an object    
function findPosY(obj) {
  var curtop = 0;
  if (obj && obj.offsetParent) {
    while (obj.offsetParent) {
      curtop += obj.offsetTop;
      obj = obj.offsetParent;
    }
  } else if (obj && obj.y) curtop += obj.y;
  return curtop;
}

// Convert HSL Color to RGB values
// @H 0->359
// @S 0->99
// @L 0->99
function HSL_to_RGB(H, S, L){
	
	function Hue_2_RGB( v1, v2, vH )  //Function Hue_2_RGB
	{
	   if ( vH < 0 )
	     vH += 1
	   if ( vH > 1 )
	     vH -= 1
	   if ( ( 6 * vH ) < 1 )
	     return ( v1 + ( v2 - v1 ) * 6 * vH )
	   if ( ( 2 * vH ) < 1 )
	     return ( v2 )
	   if ( ( 3 * vH ) < 2 )
	     return ( v1 + ( v2 - v1 ) * ( ( 2 / 3 ) - vH ) * 6 )
	   
	   return ( v1 )
	}
	
	 H = H / 360;
     S = S / 100;
     L = L / 100;
		
	if ( S == 0 )                       //HSL values = 0 ÷ 1
	{
	   R = L * 255;                      //RGB results = 0 ÷ 255
	   G = L * 255;
	   B = L * 255;
	}
	else
	{
	   if ( L < 0.5 )
	   		var_2 = L * ( 1 + S );
	   else
	   		var_2 = ( L + S ) - ( S * L );
	
	   var_1 = 2 * L - var_2;
	
	   R = 255 * Hue_2_RGB( var_1, var_2, H + ( 1 / 3 ) );
	   G = 255 * Hue_2_RGB( var_1, var_2, H );
	   B = 255 * Hue_2_RGB( var_1, var_2, H - ( 1 / 3 ) );
	}
	
	RGBcolor = {};
	RGBcolor.R = parseInt(R);
	RGBcolor.G = parseInt(G);
	RGBcolor.B = parseInt(B);
	return RGBcolor;
	
}

// Convert RGB Color to HSL values
function RGB_to_HSL(R, G, B){
	
	var_R = ( R / 255 );                 //Where RGB values = 0 ÷ 255
	var_G = ( G / 255 );
	var_B = ( B / 255 );
	
	var_Min = Math.min( var_R, var_G, var_B );    //Min. value of RGB
	var_Max = Math.max( var_R, var_G, var_B );   //Max. value of RGB
	del_Max = var_Max - var_Min;             //Delta RGB value
	
	L = ( var_Max + var_Min ) / 2;
	
	if ( del_Max == 0 )                     //This is a gray, no chroma...
	{
	   H = 0;                                //HSL results = 0 ÷ 1
	   S = 0;
	}
	else                                    //Chromatic data...
	{
	   if ( L < 0.5 )
	     S = del_Max / ( var_Max + var_Min );
	   else
	     S = del_Max / ( 2 - var_Max - var_Min );
	
	   del_R = ( ( ( var_Max - var_R ) / 6 ) + ( del_Max / 2 ) ) / del_Max;
	   del_G = ( ( ( var_Max - var_G ) / 6 ) + ( del_Max / 2 ) ) / del_Max;
	   del_B = ( ( ( var_Max - var_B ) / 6 ) + ( del_Max / 2 ) ) / del_Max;
	
	   if ( var_R == var_Max )
	     H = del_B - del_G;
	   else if ( var_G == var_Max )
	     H = ( 1 / 3 ) + del_R - del_B;
	   else if ( var_B == var_Max )
	     H = ( 2 / 3 ) + del_G - del_R;
	
	   if ( H < 0 )
	     H += 1;
	   if ( H > 1 )
	     H -= 1;
	}
	HSLcolor = {};
	HSLcolor.H = parseInt(H*360);
	HSLcolor.S = parseInt(S*100);
	HSLcolor.L = parseInt(L*100);
	return HSLcolor;
}


// Update lightness field with value
function updateLightnessField(fieldName, value){
	
	lightnessFieldId = "#lightness-field_" + fieldName ;
	
	jQuery(lightnessFieldId).attr({"value" : value});
	// then update color
	updateColorField(fieldName);
}

// Update hue field with value
function updateHueField(fieldName, value){
	
	hueFieldId = "#hue-field_" + fieldName ;
	
	jQuery(hueFieldId).attr({"value" : value});
	
	// then update color
	updateColorField(fieldName);
}

// Update saturation field with value
function updateSaturationField(fieldName, value){
	
	saturationFieldId = "#saturation-field_" + fieldName
	
	jQuery(saturationFieldId).attr({"value" : value});
	
	// then update color
	/*
	 * Actually quoted because saturation and hue alway launch the event 
	 * At same time.
	 */
	//updateColorField(fieldName);
}

// Check if restore button shall appear or not
function checkRestoreButton(event){
		
	fieldId = getFieldIdFromCurrentNode(event.target);
	backupFieldId = "#restore-field_" + fieldId;
	colorFieldId = "#color-field_" + fieldId;
		
	backupValue = getHexaColor(jQuery(backupFieldId).attr('value'));
	currentValue = jQuery(colorFieldId).attr('value');
		
	if(backupValue != currentValue){
		restoreButtonId = "#smartcolor_restore_button_" + fieldId;
		jQuery(restoreButtonId).css('display', 'inline');
	}
}


// Update color field
function updateColorField(fieldName){
	
	lightnessFieldId = "#lightness-field_" + fieldName;
	hueFieldId = "#hue-field_" + fieldName;
	saturationFieldId = "#saturation-field_" + fieldName;
	
	L = jQuery(lightnessFieldId).attr("value");
	H = jQuery(hueFieldId).attr("value");
	S = jQuery(saturationFieldId).attr("value");

	RGB = HSL_to_RGB(H, S, L);
	
	R = parseInt(RGB.R).toString(16);
	if (R.length < 2)
		R = '0' + R;
	G = parseInt(RGB.G).toString(16);
	if (G.length < 2)
		G = '0' + G;
	B = parseInt(RGB.B).toString(16);
	if (B.length < 2)
		B = '0' + B;

	newValue = '#' + R + G + B;
	
	colorFieldId = "#color-field_" + fieldName
	
	jQuery(colorFieldId).attr({'value' : newValue}); 
	
	// then update sample
	updateColorSample(fieldName);
}

function updateColorSample(fieldName){
	
  colorFieldId = "#color-field_" + fieldName;
	bgValue = jQuery(colorFieldId).attr('value');
	
	sampleFieldId = "#sample_" + fieldName;
	jQuery(sampleFieldId).css({'background-color' : bgValue.toString()});
}

// Update a selector with @id to relative coord @posX @posY
// /!\ do NOTHING but moving selector to given coords
function updateSelectorPosition( sid, posX, posY){
	
	selector = jQuery("#" + sid);
		
	X = posX + 'px';
	Y = posY + 'px';
	
	jQuery(selector).css('top', Y);
	jQuery(selector).css('left', X);
}
function updateSelectorPositionX( sid, posX){
	
	selector = jQuery("#" + sid);	
	X = posX + 'px';
	jQuery(selector).css('left', X);
}
function updateSelectorPositionY( sid, posY){
	
	selector = jQuery("#" + sid);
	Y = posY + 'px';
	jQuery(selector).css('top', Y);
}

// Update a slider with @id to relative coord @posY
// /!\ do NOTHING but moving slider to given coords
function updateSliderPosition( sid, posY){
	
	slider = jQuery("#" + sid);
	Y = posY + 'px';
	jQuery(slider).css('top', Y);
}

// Find the field Id from current node
// It do so by finding x-parent with class field
// And extracting name from it id 
function getFieldIdFromCurrentNode(node){
	
	foundId = false;
	while((node.parentNode != null) && (foundId == false)){
		node = node.parentNode;
		if (jQuery(node).attr('class')=='smartcolor-container' )
			foundId = true;
	}
	if (foundId == true)
	{
		fieldId = jQuery(node).attr('id');
		// tal:attributes="id string:parent_jQuery{fieldName}
		fieldId = fieldId.substring(7, fieldId.length);
	}
	else{
		fieldId = "dummy"
	}
	return fieldId
}

function eventsCatcher(){
	
	/*
	 * View mode color sample box on mouseOver
	 */
	jQuery('.smartcolor-view-sample').mouseover(function(event){
		
		sampleColor = jQuery(this).css("background-color");

		if(jQuery.browser.msie){
			absX = event.clientX + document.documentElement.scrollLeft + document.body.scrollLeft;
			absY = event.clientY + document.documentElement.scrollTop + document.body.scrollTop;
		}
		else{
			absX = event.clientX + window.scrollX;
			absY = event.clientY + window.scrollY;
		}
				
		popup = "<div class='smartcolor-popup' style='"
		popup += "position: absolute; "
		popup += "left: " + absX +"px; "
		popup += "top: " +  absY +"px; "
		popup += "background-color: " + sampleColor  +"; "
		popup += "' >"
		popup += "&nbsp"
		popup += "</div>"
		
		jQuery("body").append(popup);
		
		/*
		 * Removed by now, was causing hugue freezes to browser
		 */
		/*
		 jQuery('.smartcolor-view-sample').mousemove(function(event){
		 	
			if(jQuery.browser.msie){
			absX = event.clientX + document.documentElement.scrollLeft + document.body.scrollLeft;
			absY = event.clientY + document.documentElement.scrollTop + document.body.scrollTop;
			}
			else{
				absX = event.clientX + window.scrollX;
				absY = event.clientY + window.scrollY;
			}
			
		 	jQuery(".smartcolor-popup").css("left",absX + "px");
			jQuery(".smartcolor-popup").css("top",absY + "px");
			
		 });
		*/
		
		 jQuery('.smartcolor-view-sample').mouseout(function(){
		 	jQuery(".smartcolor-popup").remove()
		 	jQuery('.smartcolor-view-sample').unbind('mouseout');
		 });	
	});
	
	/*
	 * Update color field
	 * Trigger color field change event
	 * Hide restore button
	 */
	jQuery(".smartcolor_restore_button").click(function(){
		fieldId = getFieldIdFromCurrentNode(this);
		backupId = "#restore-field_" + fieldId;
		oldValue = getHexaColor(jQuery(backupId).attr('value'));
		colorFieldId = "#color-field_" + fieldId;
		jQuery(colorFieldId).attr('value', oldValue);
		jQuery(colorFieldId).trigger('change');
		jQuery(this).css('display', 'none');
	});
	
	/*
	 * Toggle edit form display
	 */
	jQuery(".smartcolor_edit_button").click(function(){
		fieldId = getFieldIdFromCurrentNode(this);
		editFormId = "#smartcolor_edit_form_" + fieldId ;
		jQuery(editFormId).toggle();
	});
	
	
	/*
	 * Check if entered color if valid
	 * If so, update fields and sample
	 * Else avert user that color is incorrect
	 */
	jQuery(".color-field").change(function(){
		
		fieldId = getFieldIdFromCurrentNode(this);
		colorValue = jQuery(this).val();
		
		if (HTML_COLOR_REGEXP.test(colorValue)){
			
		}
		else 
			if(NO_SHARP_HTML_COLOR_REGEXP.test(colorValue)){
				colorValue = "#" + colorValue;
				jQuery(this).attr("value", colorValue);
			}
			else{
				colorValue = "#FFFFFF";
				jQuery(this).attr("value", colorValue);
			}
		
		// Update search form
		initColorEditFormFromField(this);
		
		// Update color sample
		updateColorSample(fieldId);
	});
	
	/*
	 * Check if entered value if valid
	 * If so, update slider and color field
	 * Else set itself to max/min value
	 */
	jQuery(".lightness-field").change(function(){
		
		fieldId = getFieldIdFromCurrentNode(this);
		
		pos = jQuery(this).attr("value");
		
		pos = parseInt(pos);
		if ( (isNaN(pos)) || (pos > 100)){
			pos = 100;
			jQuery(this).attr("value", 100);
		}
		if (pos < 0){
			pos = 0;
			jQuery(this).attr("value", 0);
		}
		
		pos = 100 - ( parseInt(pos) + s_h_offset );
		
		sliderId = "lightness-picker_" + fieldId;
		
		updateSliderPosition(sliderId, pos);
		updateColorField(fieldId);
	});
	
	jQuery(".hue-field").change(function(){
		
		fieldId = getFieldIdFromCurrentNode(this);

		pos = jQuery(this).attr("value");
		
		pos = parseInt(pos);
		if ( (isNaN(pos)) || (pos > 360)){
			pos = 360;
			jQuery(this).attr("value", 360);
		}
		if (pos < 0){
			pos = 0;
			jQuery(this).attr("value", 0);
		}
		
		pos = parseInt((parseInt(pos))/ 3.6) - c_w_offset;
		
		selectorId = "color-selector_" + fieldId; 
		
		updateSelectorPositionX(selectorId, pos);
		updateColorField(fieldId);
	});
	
	jQuery(".saturation-field").change(function(){
		
		fieldId = getFieldIdFromCurrentNode(this);
	
		pos = jQuery(this).attr("value");
		
		pos = parseInt(pos);
		if ( (isNaN(pos)) || (pos > 100)){
			pos = 100;
			jQuery(this).attr("value", 100);
		}
		if (pos < 0){
			pos = 0;
			jQuery(this).attr("value", 0);
		}
		
		pos = 100 - ( parseInt(pos) + c_h_offset );
		
		selectorId = "color-selector_" + fieldId;
		
		updateSelectorPositionY(selectorId, pos);
		updateColorField(fieldId);
	});
	
	/*
	 * Drag cursor on the color table
	 */
	jQuery(".color-selector").mousedown(function(event){
		
		jQuery(document).unbind();
		
		// Stop the event propagation to avoid color-table click event fired
		if (!event) var event = window.event;
		event.cancelBubble = true;
		if (event.stopPropagation) event.stopPropagation();
		
		fieldId = getFieldIdFromCurrentNode(this);
		
		cursorId = "#color-selector_" + fieldId;
		
		cursorPosY = jQuery(cursorId).css('top');
		cursorPosY = cursorPosY.substring(0, cursorPosY.length-2);
		cursorPosY = parseInt(cursorPosY) + c_h_offset;
		relativePosY = event.clientY;
		
		cursorPosX = jQuery(cursorId).css('left');
		cursorPosX = cursorPosX.substring(0, cursorPosX.length-2);
		cursorPosX = parseInt(cursorPosX) + c_w_offset;
		relativePosX = event.clientX;
		
		
		params = {'startPosX'  : relativePosX,
				  'startPosY'  : relativePosY,
				  'cursorPosX' : cursorPosX,
				  'cursorPosY' : cursorPosY,
				  'fieldId'   : fieldId,
				  'cursorId'  : cursorId};
				  		
		jQuery(document).bind('mousemove',params, function(event){
			
			cursorId = event.data.cursorId;
			fieldId = event.data.fieldId;
			
			cursorPosY = event.data.cursorPosY;
			startPosY = event.data.startPosY;
			movePosY = event.clientY;
			
			cursorPosX = event.data.cursorPosX;
			startPosX = event.data.startPosX;
			movePosX = event.clientX;
			
			
			newX = cursorPosX + (movePosX - startPosX) ;
			newY = cursorPosY + (movePosY - startPosY) ;
			
			if(newX < 0) newX = 0;
			if(newX >100) newX = 100;
			
			if(newY < 0) newY = 0;
			if(newY >100) newY = 100;
						
			// Update selector position
			newPosX = newX - c_w_offset;
			newPosY = newY - c_h_offset;
			
			cursorId =  "color-selector_" + fieldId
			updateSelectorPosition(cursorId, newPosX, newPosY);
			
			hueValue = parseInt(newX * 3.6)
			satValue = 100 - newY
			
			// Update fields
			updateSaturationField(fieldId, satValue);
			updateHueField(fieldId, hueValue);
						
		});
		jQuery(document).bind('mousemove',params, function(event){
			checkRestoreButton(event);	
		});
		
		// Bind mouseup to remove events handler from document
		/*
		 * FIXME : Need to remove only our events 
		 */
		jQuery(document).bind('mouseup', params, function(event){
			jQuery(document).unbind()
		});	
	});
	
	/*
	 * Move cursor to selected position on the color table
	 */
	jQuery(".color-table").mousedown(function(event){
		
		fieldId = getFieldIdFromCurrentNode(this);
		
		cornerX = findPosX(event.target)
		cornerY = findPosY(event.target)
		
		if(jQuery.browser.msie){
			absX = event.clientX + document.documentElement.scrollLeft + document.body.scrollLeft;
			absY = event.clientY + document.documentElement.scrollTop + document.body.scrollTop;
		}
		else{
			absX = event.clientX + window.scrollX;
			absY = event.clientY + window.scrollY;
		}
		relativeX = absX - cornerX;
		relativeY = absY - cornerY;
		
		// Update fields values
		saturation = 100 - relativeY;
		hue = parseInt(relativeX * 3.6);
		
		updateSaturationField(fieldId, saturation);
		updateHueField(fieldId, hue);
		
		// Update selector pos
		posX = relativeX - c_w_offset;
		posY = relativeY - c_h_offset;
		
		selectorId = "color-selector_" + fieldId;
		
		updateSelectorPosition(selectorId , posX, posY);		
								
	});
	
	/*
	 * Move slider to selected position on the light table
	 */
	jQuery(".lightness-table").mousedown(function(event){
		
		
		fieldId = getFieldIdFromCurrentNode(this);
		
		cornerY = findPosY(event.target)
		
		if(jQuery.browser.msie){
			absY = event.clientY + document.documentElement.scrollTop + document.body.scrollTop;
		}
		else{
			absY = event.clientY + window.scrollY;
		}
		
		
		relativeY = absY - cornerY;
		
		// Update fields values
		lightValue = 100 - relativeY;
		updateLightnessField(fieldId, lightValue);
		
		// Update selector pos
		posY = relativeY - s_h_offset;
		
		sliderId = "lightness-picker_" + fieldId;
		
		updateSliderPosition(sliderId , posY);
			
								
	});
	
	
	/*
	 * Move the slider on the light table
	 */
	jQuery(".lightness-slider").mousedown( function(event){
		
		jQuery(document).unbind()
		
		// Stop the event propagation to avoid light-table click event fired
		if (!event) var event = window.event;
		event.cancelBubble = true;
		if (event.stopPropagation) event.stopPropagation();
		
		fieldId = getFieldIdFromCurrentNode(this);
		
		cursorId = "#lightness-picker_" + fieldId
		
		cursorPos = jQuery(cursorId).css('top');
		cursorPos = cursorPos.substring(0, cursorPos.length-2);
		cursorPos = parseInt(cursorPos) + s_h_offset;
		
		relativePos = event.clientY;
		
		params = {'startPos'  : relativePos,
				  'cursorPos' : cursorPos,
				  'fieldId'   : fieldId,
				  'cursorId'  : cursorId};
		
		jQuery(document).bind('mousemove',params, function(event){
			
			fieldId = event.data.fieldId;
			cursorId = event.data.cursorId;
			
			cursorPos = event.data.cursorPos;
			startPos = event.data.startPos;
			movePos = event.clientY;
			new_value = cursorPos + (movePos - startPos) ;
			
			if(new_value < 0){
				new_value = 0;
			}
			if(new_value >100){
				new_value = 100;
			}
					
			// Update slider position
			newPos = new_value - s_h_offset;
			sliderId = "lightness-picker_" + fieldId;
			updateSliderPosition(sliderId, newPos)
			
			// Update field
			lightValue = 100 - new_value;
			updateLightnessField(fieldId, lightValue);
						
		});
		jQuery(document).bind('mousemove',params, function(event){
			checkRestoreButton(event);	
		});
		// Bind mouseup to remove events handler from document
		/*
		 * FIXME : Need to remove only our events 
		 */
		jQuery(document).bind('mouseup', params, function(event){
			jQuery(document).unbind()
		});
		
	});
	
	/*
	 * On all text inputs, check if restore button shall appear
	 * IMPORTANT : Handler must be set AFTER other handlers
	 * Else values won't be validated first
	 */
	jQuery(jQuery(".smartcolor-container//:text")).change(function(event){
		checkRestoreButton(event);	
	});
	jQuery(".lightness-table").mousedown(function(event){
		checkRestoreButton(event);	
	});
	jQuery(".color-table").mousedown(function(event){
		checkRestoreButton(event);	
	});
		
};

function loadSmartColorPickers() {
  jQuery('.smartcolor-container').each(function(){
     reg=new RegExp("(parent_)", "g");
     name = jQuery(this).attr('id').replace(reg,"");
     value= jQuery('#valuefor_' + name , this).val();  
     widget = '\
  \
  <div class="smartcolor_render">\
    <div>\
  		<input type="text"\
  			   class="color-field"\
  			   name="' + name + '"\
  			   value="' + value + '"\
  			   id="color-field_' + name + '" />\
  		<input type="hidden"\
  		       value="' + value + '"\
  		       name="restore-field_' + name + '"\
             id="restore-field_' + name + '" />\
		</div>\
					\
		<div class="sample"\
			   id="sample_' + name + '"\
			   style="background-color: ' + value + '">\
           &nbsp\
    </div>\
					\
		<div> \
		  <div class="smartcolor_edit_button"\
		       id="smartcolor_edit_button_' + name + '">\
							Edit Color\
			</div>\
			<div class="smartcolor_restore_button"\
				  style="display: none"\
				  id="smartcolor_restore_button_' + name + '">\
							Restore\
			</div>\
		</div>\
	</div>\
				\
	<div class="visualClear"><!-- --></div>\
				\
	<div class="smartcolor_edit_form"\
		   style="display: none"\
		   id="smartcolor_edit_form_' + name + '">\
				\
  	<!-- LIGHTNESS -->\
  	<div class="lightness"\
  	     id="lightness_' + name + '">\
  		<div class="lightness-table"\
  		     id="lightness-table_' + name + '">\
  			<div class="lightness-slider"\
  			     id="lightness-picker_' + name + '">&nbsp</div>\
  		</div>\
  	</div>\
			\
		<!-- COLOR -->\
		<div class="color"\
			   id="color_' + name + '">\
			<div class="color-table"\
			     id="color-table_' + name + '">\
				<div class="color-selector"\
				     id="color-selector_' + name + '">&nbsp</div>\
			</div>\
		</div>\
				\
		<!-- INPUTS -->\
		<div class="picker-inputs"\
		     id="picker-inputs_' + name + '">\
  		<div class="discreet">\
  			Lightness\
  		</div>\
			<div>\
				<input type="text"\
               class="lightness-field"\
               id="lightness-field_' + name + '"\
               value="0"/>\
			</div>\
			<div class="discreet">\
				Hue\
			</div>\
			<div>\
				<input type="text"\
               class="hue-field"\
               id="hue-field_' + name + '"\
               value="0"/>\
			</div>\
			<div class="discreet">\
				Saturation\
			</div>\
			<div>\
				<input type="text"\
               class="saturation-field"\
               id="saturation-field_' + name + '"\
               value="0" />\
			</div>\
		</div>\
		<div class="visualClear" style="height: 2px;"><!-- --></div>\
							\
  </div>\
   \
   ';
      jQuery(this).html(widget);    
  })
  
  jQuery(document).ready(function(){
  	initDragables();
  	eventsCatcher();
  });   
}


jQuery(document).ready(loadSmartColorPickers);

