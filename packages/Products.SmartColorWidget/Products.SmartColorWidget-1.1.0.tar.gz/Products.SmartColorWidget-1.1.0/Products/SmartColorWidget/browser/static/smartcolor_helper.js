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
AliceBlue : '#F0F8FF',
AntiqueWhite : '#FAEBD7',
Aqua : '#00FFFF',
Aquamarine : '#7FFFD4',
Azure : '#F0FFFF',
Beige : '#F5F5DC',
Bisque : '#FFE4C4',
Black : '#000000',
BlanchedAlmond : '#FFEBCD',
Blue : '#0000FF',
BlueViolet : '#8A2BE2',
Brown : '#A52A2A',
BurlyWood : '#DEB887',
CadetBlue : '#5F9EA0',
Chartreuse : '#7FFF00',
Chocolate : '#D2691E',
Coral : '#FF7F50',
CornflowerBlue : '#6495ED',
Cornsilk : '#FFF8DC',
Crimson : '#DC143C',
Cyan : '#00FFFF',
DarkBlue : '#00008B',
DarkCyan : '#008B8B',
DarkGoldenRod : '#B8860B',
DarkGray : '#A9A9A9',
DarkGrey : '#A9A9A9',
DarkGreen : '#006400',
DarkKhaki : '#BDB76B',
DarkMagenta : '#8B008B',
DarkOliveGreen : '#556B2F',
Darkorange : '#FF8C00',
DarkOrchid : '#9932CC',
DarkRed : '#8B0000',
DarkSalmon : '#E9967A',
DarkSeaGreen : '#8FBC8F',
DarkSlateBlue : '#483D8B',
DarkSlateGray : '#2F4F4F',
DarkSlateGrey : '#2F4F4F',
DarkTurquoise : '#00CED1',
DarkViolet : '#9400D3',
DeepPink : '#FF1493',
DeepSkyBlue : '#00BFFF',
DimGray : '#696969',
DimGrey : '#696969',
DodgerBlue : '#1E90FF',
FireBrick : '#B22222',
FloralWhite : '#FFFAF0',
ForestGreen : '#228B22',
Fuchsia : '#FF00FF',
Gainsboro : '#DCDCDC',
GhostWhite : '#F8F8FF',
Gold : '#FFD700',
GoldenRod : '#DAA520',
Gray : '#808080',
Grey : '#808080',
Green : '#008000',
GreenYellow : '#ADFF2F',
HoneyDew : '#F0FFF0',
HotPink : '#FF69B4',
IndianRed : '#CD5C5C',
Indigo : '#4B0082',
Ivory : '#FFFFF0',
Khaki : '#F0E68C',
Lavender : '#E6E6FA',
LavenderBlush : '#FFF0F5',
LawnGreen : '#7CFC00',
LemonChiffon : '#FFFACD',
LightBlue : '#ADD8E6',
LightCoral : '#F08080',
LightCyan : '#E0FFFF',
LightGoldenRodYellow : '#FAFAD2',
LightGray : '#D3D3D3',
LightGrey : '#D3D3D3',
LightGreen : '#90EE90',
LightPink : '#FFB6C1',
LightSalmon : '#FFA07A',
LightSeaGreen : '#20B2AA',
LightSkyBlue : '#87CEFA',
LightSlateGray : '#778899',
LightSlateGrey : '#778899',
LightSteelBlue : '#B0C4DE',
LightYellow : '#FFFFE0',
Lime : '#00FF00',
LimeGreen : '#32CD32',
Linen : '#FAF0E6',
Magenta : '#FF00FF',
Maroon : '#800000',
MediumAquaMarine : '#66CDAA',
MediumBlue : '#0000CD',
MediumOrchid : '#BA55D3',
MediumPurple : '#9370D8',
MediumSeaGreen : '#3CB371',
MediumSlateBlue : '#7B68EE',
MediumSpringGreen : '#00FA9A',
MediumTurquoise : '#48D1CC',
MediumVioletRed : '#C71585',
MidnightBlue : '#191970',
MintCream : '#F5FFFA',
MistyRose : '#FFE4E1',
Moccasin : '#FFE4B5',
NavajoWhite : '#FFDEAD',
Navy : '#000080',
OldLace : '#FDF5E6',
Olive : '#808000',
OliveDrab : '#6B8E23',
Orange : '#FFA500',
OrangeRed : '#FF4500',
Orchid : '#DA70D6',
PaleGoldenRod : '#EEE8AA',
PaleGreen : '#98FB98',
PaleTurquoise : '#AFEEEE',
PaleVioletRed : '#D87093',
PapayaWhip : '#FFEFD5',
PeachPuff : '#FFDAB9',
Peru : '#CD853F',
Pink : '#FFC0CB',
Plum : '#DDA0DD',
PowderBlue : '#B0E0E6',
Purple : '#800080',
Red : '#FF0000',
RosyBrown : '#BC8F8F',
RoyalBlue : '#4169E1',
SaddleBrown : '#8B4513',
Salmon : '#FA8072',
SandyBrown : '#F4A460',
SeaGreen : '#2E8B57',
SeaShell : '#FFF5EE',
Sienna : '#A0522D',
Silver : '#C0C0C0',
SkyBlue : '#87CEEB',
SlateBlue : '#6A5ACD',
SlateGray : '#708090',
SlateGrey : '#708090',
Snow : '#FFFAFA',
SpringGreen : '#00FF7F',
SteelBlue : '#4682B4',
Tan : '#D2B48C',
Teal : '#008080',
Thistle : '#D8BFD8',
Tomato : '#FF6347',
Turquoise : '#40E0D0',
Violet : '#EE82EE',
Wheat : '#F5DEB3',
White : '#FFFFFF',
WhiteSmoke : '#F5F5F5',
Yellow : '#FFFF00',
YellowGreen : '#9ACD32'
}

// Regexps declarations
HTML_COLOR_REGEXP = new RegExp("^([#][0-9a-fA-F]{6})$","");
NO_SHARP_HTML_COLOR_REGEXP = new RegExp("^([0-9a-fA-F]{6})$","");


// Initialise sliders and cursors position at page launch
/*
 * Should do with widget methods, but much more fun here *grin*
 */
function initDragables(){

	colorfields = jQuery(".color-field");
	for(i=0; i<colorfields.length; i++){
		// #RRGGBB
		field = colorfields[i];
		//initColorEditFormFromField(field);
		startColorWidgetFromField(field);
	}
}

// Init the whole edit form from the given color input field
// only if it is possible otherwise do nothing
function startColorWidgetFromField(field) {
    fieldValue = jQuery(field).attr('value');
    if ( fieldValue ) {
        // css colors must be changed in '#xxxxx' syntax
        if (CSS_COLORS[fieldValue]) {
            jQuery(field).val(CSS_COLORS[fieldValue]);
            initColorEditFormFromField(field);
        }
        else if (fieldValue.charAt(0)=='#') {
            // when fieldValue has only 3 digits, duplicate the 3 digits
            if  (fieldValue.length==4) {
                jQuery(field).val(fieldValue + fieldValue.substring(1,4));
                }
            if  (fieldValue.length==7) {
                initColorEditFormFromField(field);
            }
        }
    }
}


// Init the whole edit form from the given color input field
function initColorEditFormFromField(field){
	fieldId = getFieldIdFromCurrentNode(field);
	fieldValue = jQuery(field).attr('value');
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

	backupValue = jQuery(backupFieldId).attr('value');
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

	colorFieldId = "#color-field_" + fieldName
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
		oldValue = jQuery(backupId).attr('value');
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
		colorValue = jQuery(this).attr("value");

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

jQuery(document).ready(function(){
	initDragables();
	eventsCatcher();
});
