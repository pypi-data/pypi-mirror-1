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
			mapPanoramaSize: 8,
			compassSize: 40,
			arrowRotateSpeed: 60,
			angle: 0.0,
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
			drawInit: true,
			currentTile: "a",
			otherTile: "b",
			animFrame: -1,
			nrOfAnimFrames: 1,
			animAngle: 0,
			currentId: "single",
			panoramas: [],
			maps: [],
			drawMap: false
		};

		// Extend default settings
		options = $.extend(optionsDefaults, options);

		return this.each(function() {

			// Get current object
			obj = $(this);

			// Check if object is an image
			if (this.tagName.toLowerCase() == "img") {

				// Replace img with a viewer div
				obj.wrap(document.createElement("div"));
				obj = obj.parent();
			}

			// Get viewer width/height
			if (obj.attr('title') != "") {
				options.screenWidth = parseInt(obj.attr('title').split('|')[0]);
				options.screenHeight = parseInt(obj.attr('title').split('|')[1]);
			}
			obj.attr('title','');

			// Set src image
			options.orgPanHeight = $(obj.children("img")[0]).attr('height');
			options.orgPanWidth = $(obj.children("img")[0]).attr('width');

			// Get images and maps
			obj.children("img").each (function() {
				if ($(this).hasClass('roundaboutmap')) {
					var map = [];
					map.src = $(this).attr('src');
					var data = eval('(' + $(this).attr('alt') + ')');
					map.id = data.id;
					map.hotspots = [];
					map.panoramas = [];

					for (var i = 0; i < data.hotspots.length; i++) {
						var hotspot = [];
						hotspot.id = data.hotspots[i].target_map;
						hotspot.x = parseFloat(data.hotspots[i].x);
						hotspot.y = parseFloat(data.hotspots[i].y);
						hotspot.width = parseFloat(data.hotspots[i].width);
						hotspot.height = parseFloat(data.hotspots[i].height);
						map.hotspots.push(hotspot);
					}
					options.maps[map.id] = map;
					options.drawMap = true;
				} else {
					var panorama = [];
					panorama.src = $(this).attr('src');
					panorama.id = 'single';

					if ($(this).attr('alt').indexOf('{') != -1) {
						var data = eval('(' + $(this).attr('alt') + ')');
						panorama.id = data.id;
						if (options.currentId == 'single') {
							options.currentId = panorama.id;
						}
						panorama.map = data.map;
						panorama.mapx = data.mapx;
						panorama.mapy = data.mapy;
						panorama.hotspots = [];
						for (var i = 0; i < data.hotspots.length; i++) {
							var hotspot = [];
							hotspot.id = data.hotspots[i].target_image;
							hotspot.angle = parseFloat(data.hotspots[i].x_angle);
							hotspot.height = parseFloat(data.hotspots[i].y_angle);
							panorama.hotspots.push(hotspot);
						}
					}
					options.panoramas[panorama.id] = panorama;
				}
			});

			// Create map panoramas
			if (options.drawMap) {
				for (x in options.panoramas) {
					var panorama = [];
					panorama.id = x;
					panorama.x = options.panoramas[x].mapx;
					panorama.y = options.panoramas[x].mapy;
					options.maps[options.panoramas[x].map].panoramas.push(panorama);
				}
			}

			// Remove images and add class
			obj.children("img").remove();
			obj.removeClass('roundabout');
			obj.addClass('roundabout-viewer-window');

			// Calc other values
			options.orgTileWidth = parseInt(options.orgPanWidth / options.nrOfTiles);
			if (options.orgTileWidth * options.nrOfTiles < options.orgPanWidth) {
				options.orgTileWidth++;
			}
			options.lastTileWidth = options.orgTileWidth - ((options.orgTileWidth * options.nrOfTiles) - options.orgPanWidth);
			options.tileWidth = parseInt(parseFloat(options.orgTileWidth) * options.scale);
			options.panWidth = options.nrOfTiles * options.tileWidth;
			options.panHeight = parseInt(parseFloat(options.orgPanHeight) * options.scale);
			options.screenCenterX = options.screenWidth / 2;
			options.screenCenterY = options.screenHeight / 2;
			options.maxAngleX = (parseFloat(options.screenCenterX + options.hotspotSize/2) / parseFloat(options.panWidth)) * 360;
			options.speed = parseFloat(options.orgSpeed) / parseFloat(options.scale);

			// Add tiles
			for (var i = 0; i < options.nrOfTiles; i++) {
				obj.append('<div class="roundabout-tile-a"><img src="' + options.panoramas[options.currentId].src + '"/></div>');
				obj.append('<div class="roundabout-tile-b"><img src=""/></div>');
			}

			obj.children(".roundabout-tile-a, .roundabout-tile-b").css('position', 'absolute');
			obj.children(".roundabout-tile-a, .roundabout-tile-b").css('overflow', 'hidden');
			obj.children(".roundabout-tile-a").css('z-index', '4');
			obj.children(".roundabout-tile-b").css('z-index', '3');
			obj.children(".roundabout-tile-a, .roundabout-tile-b").children("img").css('position', 'absolute');
			obj.children(".roundabout-tile-a").children("img").css('z-index', '4');
			obj.children(".roundabout-tile-b").children("img").css('z-index', '3');
			obj.children(".roundabout-tile-b").hide();

			obj.append('<div class="roundabout-overlay">&nbsp;</div>');
			obj.children(".roundabout-overlay").css({
				'position': 'absolute',
				'z-index': '5',
				'background-image': 'url(++resource++collective.roundabout.images/transparent.gif)',
				'cursor': 'crosshair'
			});

			// Set screen size
			obj.width(options.screenWidth);
			obj.height(options.screenHeight);
			obj.css('overflow', 'hidden');
			obj.css('z-index', '2');
			obj.css('box-sizing', 'content-box');
			obj.css('-moz-box-sizing', 'content-box');
			obj.children(".roundabout-overlay").width(options.screenWidth);
			obj.children(".roundabout-overlay").height(options.screenHeight);

			// Setup window
			obj.wrap(document.createElement("div"));
			obj = obj.parent();
			obj.addClass('roundabout-viewer');
			obj.append('<div class="roundabout-arrow roundabout-arrow-nw">&nbsp;</div>');
			obj.append('<div class="roundabout-arrow roundabout-arrow-ne">&nbsp;</div>');
			obj.append('<div class="roundabout-arrow roundabout-arrow-se">&nbsp;</div>');
			obj.append('<div class="roundabout-arrow roundabout-arrow-sw">&nbsp;</div>');
			obj.append('<div class="roundabout-arrow roundabout-arrow-n">&nbsp;</div>');
			obj.append('<div class="roundabout-arrow roundabout-arrow-e">&nbsp;</div>');
			obj.append('<div class="roundabout-arrow roundabout-arrow-s">&nbsp;</div>');
			obj.append('<div class="roundabout-arrow roundabout-arrow-w">&nbsp;</div>');

			// Setup wrapper
			obj.wrap(document.createElement("div"));
			obj = obj.parent();
			obj.addClass('roundabout-wrapper');
			obj.data('options', options);

			// Setup map
			if (options.drawMap) {
				obj.append('<div class="roundabout-map"></div>');
				var map = $(obj.children('.roundabout-map')[0]);
				map.append('<div class="roundabout-map-window"></div>');
				map = $(map.children()[0]);
				map.append('<div class="roundabout-map-container"></div>');
				map.append('<div class="roundabout-map-overlay"></div>');
				$(map.children('.roundabout-map-overlay')[0]).append('<div class="roundabout-map-compass"></div>');
				map = $(map.children('.roundabout-map-container')[0]);
				for (x in options.maps) {
					map.append('<div id="roundabout-map-' + x + '" style="display: none"></div>');
					var curmap = $(map.children('#roundabout-map-' + x)[0]);
					curmap.append('<img id="roundabout-map-image" src="' + options.maps[x].src + '" />');

					// Add map panoramas
					var panoramas = options.maps[x].panoramas;
					for (var i = 0; i < panoramas.length; i++) {
						// Add panoramas
						curmap.append ('<div class="roundabout-map-panorama">&nbsp;</div>');
					}
					curmap.children('.roundabout-map-panorama').each(function(i) {
						$(this).css({
							top: panoramas[i].y - parseInt(options.mapPanoramaSize/2),
							left: panoramas[i].x - parseInt(options.mapPanoramaSize/2)
						});

						$(this).attr('panorama', panoramas[i].id);

						/**
						* Event handler for mousedown on map panorama, navigates to the next panorama.
						*
						* @param {Object} e			This object points to the event object.
						*/
						$(this).mousedown(function(e) {
							var obj = $($(this).parents('.roundabout-wrapper').get(0));
							var options = $(obj).data('options');

							// Hide all hotspots during anim
							$(".roundabout-hotspot", obj).hide();
							options.currentId = $(this).attr('panorama');
							obj.roundaboutGetPanorama();
							obj.find(".roundabout-tile-" + options.otherTile).roundaboutSetImage();
							options.animFrame = 0;
							options.animAngle = 0;
						});
					});

					// Add map hotspots
					var hotspots = options.maps[x].hotspots;
					for (var i = 0; i < hotspots.length; i++) {
						// Add panoramas
						curmap.append ('<div class="roundabout-map-hotspot">&nbsp;</div>');
					}
					curmap.children('.roundabout-map-hotspot').each(function(i) {
						$(this).css({
							top: hotspots[i].y,
							left: hotspots[i].x,
							width: hotspots[i].width,
							height: hotspots[i].height
						});

						$(this).attr('map', hotspots[i].id);

						/**
						* Event handler for mousedown on map hotspot, navigates to the next map.
						*
						* @param {Object} e			This object points to the event object.
						*/
						$(this).mousedown(function(e) {
							var obj = $($(this).parents('.roundabout-wrapper').get(0));
							var options = $(obj).data('options');

							// Show the right map
							obj.find('.roundabout-map-container').children().hide();
							obj.find('.roundabout-map-container').children('#roundabout-map-' + $(this).attr('map')).show();

							// Check if compass should be visible
							if (options.panoramas[options.currentId].map == $(this).attr('map')) {
								obj.find('.roundabout-map-compass').show();
							} else {
								obj.find('.roundabout-map-compass').hide();
							}
						});
					});
				}
			}

			// Draw viewer
			obj.roundaboutScaleTiles(options.scale, 'a');
			obj.roundaboutScaleTiles(options.scale, 'b');
			obj.roundaboutGetPanorama();

			/**
			* Event handler for mousedown on overlay, stores x and y coords in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find('.roundabout-overlay')).mousedown(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
					options.mouseX -= obj.find('.roundabout-viewer-window').offset().left;
					options.mouseY -= obj.find('.roundabout-viewer-window').offset().top;
				}
			});

			/**
			* Event handler for mouseup on overlay, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find('.roundabout-overlay')).mouseup(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
				var options = $(obj).data('options');

				// Set mousedown state
				options.mouseDown = false;
			});

			/**
			* Event handler for mouseout on overlay, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-overlay")).mouseout(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
				var options = $(obj).data('options');

				// Set mousedown state
//				options.mouseDown = false;
			});

			/**
			* Event handler for mouseout on arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-arrow")).mouseout(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
				var options = $(obj).data('options');

				// Set mousedown state
				options.mouseDown = false;
			});

			/**
			* Event handler for mouseover on ne arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-arrow-ne")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-arrow-se")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-arrow-sw")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-arrow-nw")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-arrow-n")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-arrow-e")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-arrow-s")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-arrow-w")).mouseover(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
			$(obj.find(".roundabout-overlay")).mousemove(function(e) {
				var obj = $($(this).parents('.roundabout-wrapper').get(0));
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
				options.mouseX -= obj.find('.roundabout-viewer-window').offset().left;
				options.mouseY -= obj.find('.roundabout-viewer-window').offset().top;
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

					obj.roundaboutScaleTiles(options.scale, 'a');
					obj.roundaboutScaleTiles(options.scale, 'b');
					options.drawScale = false;
				}

				var prevAngle = options.angle;
				var prevHeight = options.height;

				// Update angle/height
				if (options.mouseDown) {
					
					// Recalc behavior
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

				if (options.animFrame != -1) {
					var animScale = options.scale + parseFloat(options.animFrame)/options.nrOfAnimFrames*options.scale;
					var animFactor = parseFloat(options.animFrame)/parseFloat(options.nrOfAnimFrames);
					if (options.animFrame < options.nrOfAnimFrames/4) {
						options.angle -= options.animAngle*animFactor/parseFloat(options.nrOfAnimFrames)*8;
					}

					obj.roundaboutScaleTiles(animScale, options.currentTile);
					$(obj).roundaboutDrawTiles (options.currentTile, animScale);
					$(obj).roundaboutDrawTiles (options.otherTile, options.scale);
				} else {
					if (drawObjects == true) {
						$(obj).roundaboutDrawTiles (options.currentTile, options.scale);

						// Set compass
						if (options.drawMap) {
							var img = ['n','ne','e','se','s','sw','w','nw'][parseInt((options.angle+22.5)%360/45)];
							var compass = $(obj).find('.roundabout-map-compass');
							if (!compass.hasClass('roundabout-map-compass-' + img)) {
								compass.removeClass().addClass('roundabout-map-compass').addClass('roundabout-map-compass-' + img);
							}
						}
					}
				}

				// Check if map available
				if (options.drawMap) {

					// Draw hotspots
					var oHotspot;
					if (typeof(options.panoramas[options.currentId]) != 'undefined') {
						if (((options.animFrame == -1) && (drawObjects == true)) || (options.animFrame == options.nrOfAnimFrames)) {
							for (var iCount = 0; iCount < options.panoramas[options.currentId].hotspots.length; iCount++) {
								oHotspot = options.panoramas[options.currentId].hotspots[iCount];

								// Check if left from center
								var fDifangle = (options.angle - oHotspot.angle + 360) % 360;
								var hotspotobj = $($(obj).find(".roundabout-overlay")).children(".roundabout-hotspot")[iCount];

								var fCalcAngle;
								if (options.angle < options.maxAngleX) {
									fCalcAngle = options.angle + 360;
								} else {
									fCalcAngle = options.angle;
								}
								if ((fDifangle >= 0) && (fDifangle < options.maxAngleX)) {
									var fFactor = fDifangle / options.maxAngleX;

									$(hotspotobj).css ("left", options.screenCenterX - parseInt (fFactor * (options.screenCenterX+options.hotspotSize/2)) - options.hotspotSize / 2);
									$(hotspotobj).css ("top", parseInt(oHotspot.height * parseFloat(options.panHeight)) - parseInt(options.height * (options.panHeight - options.screenHeight)) - options.hotspotSize / 2);
									$(hotspotobj).show();

								// Check if right from center
								} else if ((fDifangle <= 360) && (fDifangle > 360 - options.maxAngleX)) {

									var fFactor = (360 - fDifangle) / options.maxAngleX;
									$(hotspotobj).css ("left", options.screenCenterX + parseInt (fFactor * (options.screenCenterX + options.hotspotSize/2)) - options.hotspotSize / 2);
									$(hotspotobj).css ("top", parseInt(oHotspot.height * parseFloat(options.panHeight)) - parseInt(options.height * (options.panHeight - options.screenHeight)) - options.hotspotSize / 2);
									$(hotspotobj).show();

								} else {

									// Hide hotspot
									$(hotspotobj).hide();
								}
							}
						}
					}
				}

				if (options.animFrame != -1) {
					if (options.animFrame == options.nrOfAnimFrames) {

						// Hide current frame
						obj.find(".roundabout-tile-" + options.currentTile).hide();
						obj.find(".roundabout-tile-" + options.currentTile).css("opacity", 1);
						obj.find(".roundabout-tile-" + options.currentTile).css("z-index", 3);
						obj.find(".roundabout-tile-" + options.otherTile).css("z-index", 4);

						// Reset scale
						obj.roundaboutScaleTiles(options.scale, options.currentTile);

						var sTemp = options.currentTile;
						options.currentTile = options.otherTile;
						options.otherTile = sTemp;

						// End anim
						options.animFrame = -1;
					} else {
						options.animFrame++;
					}
				}
			});
		});
	};

	/**
	* Scale the specified tiles.
	*
	* @param {Float} newScale	New scale factor.
 	* @param {String} tile		Specifies which tiles must be draw, can be either 'a' or 'b'
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutScaleTiles = function(newScale, tile) {
		var obj = $(this);
		var options = $(this).data('options');
		var tiles = obj.find('.roundabout-tile-' + tile);

		var newWidth = parseInt(parseFloat(options.orgTileWidth) * newScale);
		var newWidthLast = parseInt(parseFloat(options.lastTileWidth) * newScale);
		var newHeight = parseInt(parseFloat(options.orgPanHeight) * newScale);

		// ### TODO: Scale images not just div's
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
	* Set the image of the specified tile.
	*
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutSetImage = function() {
		var obj = $($(this).parents('.roundabout-wrapper').get(0));
		var options = $(obj).data('options');
		return this.each(function() {
			$(this).children("img").attr("src", options.panoramas[options.currentId].src);
		});
	};

	/**
	* Draw the specified tiles with the specified scale.
	*
 	* @param {String} tile		Specifies which tiles must be draw, can be either 'a' or 'b'
	* @param {Float} localScale	The scale of the tiles to be drawn.
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutDrawTiles = function(tile, localScale) {
		var obj = $(this);
		var options = $(this).data('options');
		var tiles = obj.find('.roundabout-tile-' + tile);

		iLocalTileWidth = parseInt(parseFloat(options.orgTileWidth) * localScale);
		iLocalTileWidthLast = parseInt(parseFloat(options.lastTileWidth) * localScale);
		iLocalPanWidth = options.nrOfTiles * options.tileWidth;
		iLocalPanHeight = parseInt(parseFloat(options.orgPanHeight) * localScale);
		fLocalMaxAngleX = (parseFloat(options.screenCenterX + options.hotspotSize/2) / parseFloat(options.panWidth)) * 360;

		// Check if animation
		var bAnim = ((options.animFrame != -1) && (tile == options.currentTile))?true:false;
		var fAnimFactor = parseFloat(options.nrOfAnimFrames-options.animFrame)/options.nrOfAnimFrames;

		var fLocalAngle = options.angle;
		if (bAnim) {
			fLocalAngle -= (options.animAngle*(1-fAnimFactor));
		}

		// Draw center tile
		var iTile = parseInt(fLocalAngle/360*options.nrOfTiles);
		var fLocalAngle = fLocalAngle/360*options.nrOfTiles-iTile;
		var iX = options.screenCenterX;
		iX -= parseInt(fLocalAngle*iLocalTileWidth);
		var iY = parseInt((iLocalPanHeight-options.screenHeight)*-options.height);

		$(tiles[iTile]).css("left", iX);
		$(tiles[iTile]).css("top", iY);
		$(tiles[iTile]).show();
		if (bAnim) {
			$(tiles[iTile]).css("opacity", fAnimFactor);
		}

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
			if (bAnim) {
				$(tiles[iCurTile]).css("opacity", fAnimFactor);
			}
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
			if (bAnim) {
				$(tiles[iCurTile]).css("opacity", fAnimFactor);
			}
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

	/**
	* Get the current panorama data from the backend.
	*
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutGetPanorama = function() {
		var obj = $(this);
		var options = $(this).data('options');

		// Check if maps available
		if (options.drawMap) {
			
			// Clear hotspots
			var overlay = $(obj).find('.roundabout-overlay');
			$(overlay).empty();

			// Add hotspots
			for (var i = 0; i < options.panoramas[options.currentId].hotspots.length; i++) {
				// Add hotspot
				$(overlay).append ("<div class=\"roundabout-hotspot\" style=\"position: absolute; left: 1000px; cursor: pointer; display: none;\">&nbsp;</div>");
			}

			// Store data
			$(".roundabout-hotspot", overlay).each(function(i) {
				$(this).attr('hotspot', options.panoramas[options.currentId].hotspots[i].id + "|" + options.panoramas[options.currentId].hotspots[i].angle);

				/**
				* Event handler for mousedown on hotspot, navigates to the next panorama.
				*
				* @param {Object} e			This object points to the event object.
				*/
				$(this).mousedown(function(e) {
					var obj = $($(this).parents('.roundabout-wrapper').get(0));
					var options = $(obj).data('options');

					// Hide all hotspots during anim
					$(".roundabout-hotspot", obj).hide();

					options.currentId = $(this).attr('hotspot').split('|')[0];
					obj.roundaboutGetPanorama();
					obj.find(".roundabout-tile-" + options.otherTile).roundaboutSetImage();
					options.animFrame = 0;
					options.animAngle = (options.angle - parseFloat($(this).attr('hotspot').split('|')[1]) + 360) % 360;
					if (options.animAngle > 180) { options.animAngle -= 360; }
				});
			});

			obj.find('.roundabout-map-container').children().hide();
			obj.find('.roundabout-map-container').children('#roundabout-map-' + options.panoramas[options.currentId].map).show();
			obj.find('.roundabout-map-compass').show();

			// Reposition compass
			obj.find('.roundabout-map-compass').css({
				left: options.panoramas[options.currentId].mapx - parseInt(options.compassSize/2),
				top: options.panoramas[options.currentId].mapy - parseInt(options.compassSize/2)
			});
		}
	};
})(jQuery);
