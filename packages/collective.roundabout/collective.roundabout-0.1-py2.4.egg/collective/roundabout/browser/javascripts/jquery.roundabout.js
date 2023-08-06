/**
 * jQuery.roundabout
 * Copyright (c) 2008 Four Digits - rob@fourdigits.nl
 * 
 * @projectDescription	This plugin is used to view a virtual tour with panorama photo's.
 * @author				Rob Gietema
 * @version				0.1
 *
 * @id jQuery.roundabout
 * @id jQuery.fn.roundabout
 */
;(function($) {

	/**
	* Create a new instance of roundabout.
	*
	* @classDescription			This class creates a new roundabout object.
	* @param {Object} options	This object contains the options used for the roundabout object.
	* @return {Object}			Returns a new roundabout object.
	* @type {Object}
	* @constructor
	*/
	$.fn.roundabout = function(options) {

		// Option default values
		var optionsDefaults = {
			screenWidth: 320,
			screenHeight: 240,
			scale: 1,
			hotspotSize: 28,
			arrowRotateSpeed: 60,
			angle: 300.0,
			height: 0.5,
			deadZone: 25,
			orgSpeed: 10,
			mouseDown: false,
			mouseX: 0,
			mouseY: 0,
			drawScale: false,
			nrOfTiles: 12,
			orgTileWidth: 0,
			orgPanHeight: 0,
			orgPanWidth: 0,
			drawInit: true
		};

		// Extend default settings
		options = $.extend(optionsDefaults, options);


		return this.each(function() {

			// Get current object
			obj = $(this);

			// Set src image
			options.imageSrc = obj.attr('src');
			options.orgPanHeight = obj.height();
			options.orgPanWidth = obj.width();
			options.orgTileWidth = parseInt(options.orgPanWidth / options.nrOfTiles);

			if (options.orgTileWidth * options.nrOfTiles < options.orgPanWidth) {
				options.orgTileWidth++;
			}
			options.lastTileWidth = options.orgTileWidth - ((options.orgTileWidth * options.nrOfTiles) - options.orgPanWidth);

			// Calc other values
			options.tileWidth = parseInt(parseFloat(options.orgTileWidth) * options.scale);
			options.panWidth = options.nrOfTiles * options.tileWidth;
			options.panHeight = parseInt(parseFloat(options.orgPanHeight) * options.scale);
			options.screenCenterX = options.screenWidth / 2;
			options.screenCenterY = options.screenHeight / 2;
			options.maxAngleX = (parseFloat(options.screenCenterX + options.hotspotSize/2) / parseFloat(options.panWidth)) * 360;
			options.speed = parseFloat(options.orgSpeed) / parseFloat(options.scale);

			// Replace img with a viewer div
			obj.wrap(document.createElement("div"));
			obj = obj.parent();
			obj.wrap(document.createElement("div"));
			obj.children("img").remove();
			obj.addClass('roundabout-container');

			// Add default values
			obj.data('options', options);

			// Add tiles
			for (var i = 0; i < options.nrOfTiles; i++) {
				obj.append('<div class="roundabout-tile"><img src="' + options.imageSrc + '"/></div>');
			}

			obj.children(".roundabout-tile").css('position', 'absolute');
			obj.children(".roundabout-tile").css('overflow', 'hidden');
			obj.children(".roundabout-tile").css('z-index', '3');
			obj.children(".roundabout-tile").children("img").css('position', 'absolute');
			obj.children(".roundabout-tile").children("img").css('z-index', '3');

			obj.append('<div class="roundabout-overlay">&nbsp;</div>');
			obj.children(".roundabout-overlay").css({
				'position': 'absolute',
				'z-index': '5',
				'background-image': 'url(++resource++collective.roundabout.images/transparent.gif)',
				'cursor': 'crosshair'
			});

			obj.roundaboutScaleTiles(options.scale);

			// Set screen size
			obj.width(options.screenWidth);
			obj.height(options.screenHeight);
			obj.css('overflow', 'hidden');
			obj.css('z-index', '2');
			obj.css('box-sizing', 'content-box');
			obj.css('-moz-box-sizing', 'content-box');

			obj.parent().addClass('roundabout-wrapper');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-nw">&nbsp;</div>');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-ne">&nbsp;</div>');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-se">&nbsp;</div>');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-sw">&nbsp;</div>');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-n">&nbsp;</div>');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-e">&nbsp;</div>');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-s">&nbsp;</div>');
			obj.parent().append('<div class="roundabout-arrow roundabout-arrow-w">&nbsp;</div>');

			obj.children(".roundabout-overlay").width(options.screenWidth);
			obj.children(".roundabout-overlay").height(options.screenHeight);

			/**
			* Event handler for mousedown on overlay, stores x and y coords in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.children('.roundabout-overlay')).mousedown(function(e) {
				var obj = $($(this).get(0)).parent();
				var options = $(obj).data('options');

				// Check classname of event object
				if (e.target.className == 'roundabout-overlay') {

					// Set mousedown state
					options.mouseDown = true;

					// Set event object
					if (!e) {
						e = window.event;
					}

					// Check get x and y coords
					if (e.pageX || e.pageY) {
						options.mouseX = e.pageX;
						options.mouseY = e.pageY;
					} else if (e.clientX || e.clientY) {
						options.mouseX = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
						options.mouseY = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
					}
					options.mouseX -= obj.offset().left;
					options.mouseY -= obj.offset().top;
				}
			});

			/**
			* Event handler for mouseup on overlay, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.children('.roundabout-overlay')).mouseup(function(e) {
				var obj = $($(this).get(0)).parent();
				var options = $(obj).data('options');

				// Set mousedown state
				options.mouseDown = false;
			});

			/**
			* Event handler for mouseout on overlay, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.children(".roundabout-overlay")).mouseout(function(e) {
				var obj = $($(this).get(0)).parent();
				var options = $(obj).data('options');

				// Set mousedown state
//				options.mouseDown = false;
			});

			/**
			* Event handler for mouseout on arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow")).mouseout(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mousedown state
				options.mouseDown = false;
			});

			/**
			* Event handler for mouseover on ne arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-ne")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX + options.arrowRotateSpeed;
				options.mouseY = options.screenCenterY - options.arrowRotateSpeed;
			});

			/**
			* Event handler for mouseover on se arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-se")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX + options.arrowRotateSpeed;
				options.mouseY = options.screenCenterY + options.arrowRotateSpeed;
			});

			/**
			* Event handler for mouseover on sw arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-sw")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX - options.arrowRotateSpeed;
				options.mouseY = options.screenCenterY + options.arrowRotateSpeed;
			});

			/**
			* Event handler for mouseover on nw arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-nw")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX - options.arrowRotateSpeed;
				options.mouseY = options.screenCenterY - options.arrowRotateSpeed;
			});

			/**
			* Event handler for mouseover on n arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-n")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX;
				options.mouseY = options.screenCenterY - options.arrowRotateSpeed;
			});

			/**
			* Event handler for mouseover on e arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-e")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX + options.arrowRotateSpeed;
				options.mouseY = options.screenCenterY;
			});

			/**
			* Event handler for mouseover on s arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-s")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX;
				options.mouseY = options.screenCenterY + options.arrowRotateSpeed;
			});

			/**
			* Event handler for mouseover on w arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.parent().children(".roundabout-arrow-w")).mouseover(function(e) {
				var obj = $($(this).get(0)).parent().children(".roundabout-container");
				var options = $(obj).data('options');

				// Set mouse states
				options.mouseDown = true;
				options.mouseX = options.screenCenterX - options.arrowRotateSpeed;
				options.mouseY = options.screenCenterY;
			});

			/**
			* Event handler for mousemove on overlay, stores x and y coords in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.children(".roundabout-overlay")).mousemove(function(e) {
				var obj = $($(this).get(0)).parent();
				var options = $(obj).data('options');

				// Set mousedown state
				if (!e) {
					e = window.event;
				}
				if (e.pageX || e.pageY) {
					options.mouseX = e.pageX;
					options.mouseY = e.pageY;
				} else if (e.clientX || e.clientY) {
					options.mouseX = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
					options.mouseY = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
				}
				options.mouseX -= obj.offset().left;
				options.mouseY -= obj.offset().top;
			});

			/**
			* Main draw loop which is executed every 50ms.
			*/
			obj.everyTime(50,function() {
				var obj = $(this);
				var options = $(this).data('options');

				// If scale tiles
				if (options.drawScale == true) {
					options.tileWidth = parseInt(parseFloat(options.orgTileWidth) * options.scale);
					options.panWidth = options.nrOfTiles * options.tileWidth;
					options.panHeight = parseInt(parseFloat(options.orgPanHeight) * options.scale);
					options.maxAngleX = (parseFloat(options.screenCenterX + options.hotspotSize/2) / parseFloat(options.panWidth)) * 360;
					options.speed = parseFloat(options.orgSpeed) / parseFloat(options.scale);

					obj.roundaboutScaleTiles(options.scale);
					options.drawScale = false;
				}

				var prevAngle = options.angle;
				var prevHeight = options.height;

				// Update angle/height
				if (options.mouseDown) {
					
					// Recalc behavior
					options.behaviorfactor -= options.behaviorinfluence/30;
					if (options.behaviorfactor < 0) { options.behaviorfactor = 0; }
	
					if (options.mouseX > options.screenCenterX+options.deadZone) {
						options.angle += (options.mouseX-options.screenCenterX-options.deadZone)/(options.screenCenterX-options.deadZone)*options.speed;
					}

					if (options.mouseX < options.screenCenterX-options.deadZone) {
						options.angle -= (options.screenCenterX-options.mouseX-options.deadZone)/(options.screenCenterX-options.deadZone)*options.speed;
					}

					if (options.angle > 360) { options.angle -= 360; }
					if (options.angle < 0) { options.angle += 360; }

					if (options.mouseY > options.screenCenterY+options.deadZone) {
						options.height += (options.mouseY-options.screenCenterY-options.deadZone)/(options.screenCenterY-options.deadZone)*options.speed/50;
					}

					if (options.mouseY < options.screenCenterY-options.deadZone) {
						options.height -= (options.screenCenterY-options.mouseY-options.deadZone)/(options.screenCenterY-options.deadZone)*options.speed/50;
					}

					if (options.height < 0) { options.height = 0; }
					if (options.height > 1) { options.height = 1; }
				}

				var drawObjects = false;
				if (options.drawInit == true) {
					drawObjects = true;
					options.drawInit = false;
				} else if ((options.angle != prevAngle) || (options.height != prevHeight)) {
					drawObjects = true;
				}

				if (drawObjects == true) {
					$(obj).roundaboutDrawTiles (options.scale);
				}
			});
		});
	};

	/**
	* Scale the specified tiles.
	*
	* @param {Float} newScale	New scale factor.
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutScaleTiles = function(newScale) {
		var obj = $(this);
		var options = $(this).data('options');
		var tiles = obj.children('.roundabout-tile');

		var newWidth = parseInt(parseFloat(options.orgTileWidth) * newScale);
		var newWidthLast = parseInt(parseFloat(options.lastTileWidth) * newScale);
		var newHeight = parseInt(parseFloat(options.orgPanHeight) * newScale);

		for (var iTile=0;iTile<options.nrOfTiles;iTile++) {
			if (iTile == options.nrOfTiles - 1) {
				$(tiles[iTile]).children("img").css("left", -1 * newWidth * iTile + 1);
				$(tiles[iTile]).width(newWidthLast);
			} else {
				$(tiles[iTile]).children("img").css("left", -1 * newWidth * iTile);
				$(tiles[iTile]).width(newWidth);
			}
			$(tiles[iTile]).height(newHeight);
		}
	};

	/**
	* Draw the specified tiles with the specified scale.
	*
	* @param {Float} localScale	The scale of the tiles to be drawn.
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutDrawTiles = function(localScale) {
		var obj = $(this);
		var options = $(this).data('options');
		var tiles = obj.children('.roundabout-tile');

		iLocalTileWidth = parseInt(parseFloat(options.orgTileWidth) * localScale);
		iLocalTileWidthLast = parseInt(parseFloat(options.lastTileWidth) * localScale);
		iLocalPanWidth = options.nrOfTiles * options.tileWidth;
		iLocalPanHeight = parseInt(parseFloat(options.orgPanHeight) * localScale);
		fLocalMaxAngleX = (parseFloat(options.screenCenterX + options.hotspotSize/2) / parseFloat(options.panWidth)) * 360;

		var fLocalAngle = options.angle;

		// Draw center tile
		var iTile = parseInt(fLocalAngle/360*options.nrOfTiles);
		var fLocalAngle = fLocalAngle/360*options.nrOfTiles-iTile;
		var iX = options.screenCenterX;
		iX -= parseInt(fLocalAngle*iLocalTileWidth);
		var iY = parseInt((iLocalPanHeight-options.screenHeight)*-options.height);

		$(tiles[iTile]).css("left", iX);
		$(tiles[iTile]).css("top", iY);
		$(tiles[iTile]).show();

		// Draw tiles right from current
		var iCurX = iX;
		var iCurTile = iTile;

		while (iCurX + iLocalTileWidth < options.screenWidth) {
			if (iCurTile == options.nrOfTiles-1) {
				iCurTile = 0;
				iCurX += iLocalTileWidthLast;
			} else {
				iCurTile++;
				iCurX += iLocalTileWidth;
			}

			$(tiles[iCurTile]).css("left", iCurX);
			$(tiles[iCurTile]).css("top", iY);
			$(tiles[iCurTile]).show();
		}
		var iRightTile = iCurTile;

		// Draw tiles left from current
		var iCurX = iX;
		var iCurTile = iTile;
		while (iCurX > iLocalTileWidth * -1) {
			if (iCurTile == 0) {
				iCurTile = options.nrOfTiles-1;
				iCurX -= iLocalTileWidthLast;
			} else {
				iCurTile--;
				iCurX -= iLocalTileWidth;
			}

			$(tiles[iCurTile]).css("left", iCurX);
			$(tiles[iCurTile]).css("top", iY);
			$(tiles[iCurTile]).show();
		}

		// Hide the rest of the tiles
		while (iCurTile != iRightTile) {
			$(tiles[iCurTile]).hide();
			if (iCurTile == 0) {
				iCurTile = options.nrOfTiles-1;
			} else {
				iCurTile--;
			}
		}
	};
})(jQuery);
