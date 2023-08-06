/**
 * jQuery.roundabout
 * Copyright (c) 2008 Four Digits - rob@fourdigits.nl
 * 
 * @projectDescription	This plugin is used to view a virtual tour with panoramic images.
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
			screenWidth: 320,			// Viewer width
			screenHeight: 240,			// Viewer height
			scale: 1,					// Image scale
			hotspotSize: 28,			// Width / height of the hotspots
			mapPanoramaSize: 8,			// Width / height of panorama points on the map
			compassSize: 40,			// Width / height of the compass
			arrowRotateSpeed: 60,		// Rotate speed when hovering over arrows around the viewer
			angle: 0.0,					// Current image x-angle
			height: 0.5,				// Current image y-angle
			deadZone: 25,				// Deadzone in the center of the image
			orgSpeed: 10,				// Original speed with original scale
			mouseDown: false,			// Mouse down state
			mouseX: 0,					// Mouse x-coordinate relative to viewer window
			mouseY: 0,					// Mouse y-coordinate relative to viewer window
			drawScale: false,			// True if tiles need to be scaled
			nrOfTiles: 12,				// Number of tiles
			orgTileWidth: 0,			// Original tile width
			orgPanHeight: 0,			// Original panoramic image height
			orgPanWidth: 0,				// Original panoramic image width
			drawInit: true,				// True if init needs to be run
			currentTile: "a",			// Current tile set
			otherTile: "b",				// Other (not active) tile set
			animFrame: -1,				// Current animation frame (-1 if not in an animation)
			nrOfAnimFrames: 10,			// Number of animation frames between image transitions
			animAngle: 0,				// X-angle of animation between image transitions
			currentId: "single",		// Current image id
			panoramas: [],				// Array of panorama data
			maps: [],					// Array of map data
			drawMap: false,				// True if map is available
			nrOfPanoramas: 0,			// Number of panoramas
			stopOnMouseOut: false		// True if rotating must stop when leaving the viewer window
		};

		// Extend default settings
		options = $.extend(optionsDefaults, options);

		// Loop through matched elements
		return this.each(function() {

			// Get current object
			obj = $(this);

			// Check if object is an image
			if (this.tagName.toLowerCase() == "img") {

				// Replace img with a viewer div
				obj = obj
					.removeClass()
					.addClass("roundaboutimage")
					.wrap(document.createElement("div"))
					.parent();
			}

			// Get viewer width / height and start image / angle
			if (obj.attr("title") != "") {

				// Get json data
				var data = eval("(" + obj.attr("title") + ")");

				// Set viewer width / height
				options.screenWidth = parseInt(data.viewer_width);
				options.screenHeight = parseInt(data.viewer_height);

				// Set start image / angle
				if (data.start_image != "None")
					options.currentId = data.start_image;
				options.angle = parseFloat(data.start_angle);

				options.nrOfAnimFrames = parseInt(data.animation_frames);
				if (options.nrOfAnimFrames < 1)
					options.nrOfAnimFrames = 1;
			}

			// Reset title
			obj.attr("title","");

			// Get image width / height
			options.orgPanHeight = $(obj.children("img")[0]).height();
			options.orgPanWidth = $(obj.children("img")[0]).width();

			// Get maps
			obj.children("img.roundaboutmap").each (function() {

				// Get map data and add to maps attribute
				var map = {
					src: $(this).attr("src"),
					panoramas: []
				};
				map = $.extend(map, eval("(" + $(this).attr("title") + ")"));
				options.maps[map.id] = map;

				// Draw map
				options.drawMap = true;
			});

			// Get images
			options.nrOfPanoramas = 0;
			obj.children("img.roundaboutimage").each (function() {

				// Default panoramic image data
				var panorama = {
					src: $(this).attr("src"),		// Src of image
					id: "single"					// Id of image
				};

				// Add json data if available
				if ($(this).attr("title").indexOf("{") != -1)
					panorama = $.extend(panorama, eval("(" + $(this).attr("title") + ")"));

				// Set current id if not set
				if (options.currentId == "single")
					options.currentId = panorama.id;

				// Add panorama to panorama list
				options.panoramas[panorama.id] = panorama;

				// If map is available
				if (options.drawMap) {

					// Add panorama location to map array
					options.maps[panorama.map].panoramas.push({
						id: panorama.id,
						x: panorama.mapx,
						y: panorama.mapy
					});
				}

				// Inc number of panoramas
				options.nrOfPanoramas++;
			});

			// If no panorama images available exit
			if (options.nrOfPanoramas == 0)
				return;

			// Remove images and add class
			obj.children().remove();
			obj
				.removeClass("roundabout")
				.addClass("roundabout-viewer-window");

			// Calc other values
			options.orgTileWidth = Math.ceil(options.orgPanWidth / options.nrOfTiles);
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
				obj
					.append(
						$(document.createElement("div"))
							.addClass("roundabout-tile-a")
							.append(
								$(document.createElement("img"))
									.attr("src", options.panoramas[options.currentId].src)
							)
					)
					.append(
						$(document.createElement("div"))
							.addClass("roundabout-tile-b")
							.append(
								$(document.createElement("img"))
							)
					)
			}

			// Add overlay
			obj.append(
				$(document.createElement("div"))
					.addClass("roundabout-overlay")
					.html("&nbsp;")
			);

			// Set screen size
			obj
				.width(options.screenWidth)
				.height(options.screenHeight);
			obj.children(".roundabout-overlay")
				.width(options.screenWidth)
				.height(options.screenHeight);

			// Setup viewer
			obj = obj
				.wrap(document.createElement("div"))
				.parent()
				.addClass("roundabout-viewer");

			// Add arrows
			$(["nw","ne","se","sw","n","e","s","w"]).each(function() {
				obj.append(
					$(document.createElement("div"))
						.addClass("roundabout-arrow")
						.addClass("roundabout-arrow-" + this)
						.html("&nbsp;")
				);
			});

			// Setup wrapper
			obj = obj
				.wrap(document.createElement("div"))
				.parent()
				.addClass("roundabout-wrapper")
				.data("options", options);

			// Setup map
			if (options.drawMap) {
				obj.append('<div class="roundabout-map"></div>');
				var map = $(obj.children(".roundabout-map")[0]);
				map.append('<div class="roundabout-map-window"></div>');
				map = $(map.children()[0]);
				map.append('<div class="roundabout-map-container"></div>');
				map.append('<div class="roundabout-map-overlay"></div>');
				$(map.children(".roundabout-map-overlay")[0]).append('<div class="roundabout-map-compass">&nbsp;</div>');
				map = $(map.children(".roundabout-map-container")[0]);
				for (x in options.maps) {
					if (typeof(options.maps[x]) == 'object') {
						map.append('<div id="roundabout-map-' + x + '"></div>');
						var curmap = $(map.children("#roundabout-map-" + x)[0]);
						curmap.append('<img id="roundabout-map-image" src="' + options.maps[x].src + '" />');

						// Add map panoramas
						var panoramas = options.maps[x].panoramas;
						for (var i = 0; i < panoramas.length; i++) {
							// Add panoramas
							curmap.append ('<div class="roundabout-map-panorama">&nbsp;</div>');
						}
						curmap.children(".roundabout-map-panorama").each(function(i) {
							$(this).css({
								top: panoramas[i].y - parseInt(options.mapPanoramaSize/2),
								left: panoramas[i].x - parseInt(options.mapPanoramaSize/2)
							});

							$(this).data("panorama", panoramas[i].id);

							/**
							* Event handler for mousedown on map panorama, navigates to the next panorama.
							*
							* @param {Object} e			This object points to the event object.
							*/
							$(this).mousedown(function(e) {
								var obj = $($(this).parents(".roundabout-wrapper").get(0));
								var options = $(obj).data("options");

								// Hide all hotspots during anim
								$(".roundabout-hotspot", obj).hide();
								options.currentId = $(this).data("panorama");
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
						curmap.children(".roundabout-map-hotspot").each(function(i) {
							$(this).css({
								top: hotspots[i].y,
								left: hotspots[i].x,
								width: hotspots[i].width,
								height: hotspots[i].height
							});

							$(this).data("map", hotspots[i].target_map);

							/**
							* Event handler for mousedown on map hotspot, navigates to the next map.
							*
							* @param {Object} e			This object points to the event object.
							*/
							$(this).mousedown(function(e) {
								var obj = $($(this).parents(".roundabout-wrapper").get(0));
								var options = $(obj).data("options");

								// Show the right map
								obj.find(".roundabout-map-container").children().hide();
								obj.find(".roundabout-map-container").children("#roundabout-map-" + $(this).data("map")).show();

								// Check if compass should be visible
								if (options.panoramas[options.currentId].map == $(this).data("map")) {
									obj.find(".roundabout-map-compass").show();
								} else {
									obj.find(".roundabout-map-compass").hide();
								}
							});
						});
					}
				}
			}

			// Draw viewer
			obj
				.roundaboutScaleTiles(options.scale, "a")
				.roundaboutScaleTiles(options.scale, "b")
				.roundaboutGetPanorama();

			/**
			* Event handler for mousedown on overlay, stores x and y coords in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-overlay")).mousedown(function(e) {

				// Check classname of event object
				if (e.target.className == "roundabout-overlay") {

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
					options.mouseX -= obj.find(".roundabout-viewer-window").offset().left;
					options.mouseY -= obj.find(".roundabout-viewer-window").offset().top;
				}
				
				// Prevent selection
				return false;
			});

			/**
			* Event handler for mouseup on overlay, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-overlay")).mouseup(function(e) {

				// Set mousedown state
				options.mouseDown = false;
			});

			/**
			* Event handler for mouseout on overlay, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-overlay")).mouseout(function(e) {

				// Set mousedown state
				if (options.stopOnMouseOut)
					options.mouseDown = false;
			});

			/**
			* Event handler for mouseout on arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-arrow")).mouseout(function(e) {

				// Set mousedown state
				options.mouseDown = false;
			});

			/**
			* Event handler for mouseover on arrow, sets mousestate in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-arrow")).mouseover(function(e) {

				// Set mousedown state
				options.mouseDown = true;
				options.mouseX = options.screenCenterX;
				options.mouseY = options.screenCenterY;

				// Get arrow and add rotate speed
				var arrow =$(this).attr("class").split("roundabout-arrow-")[1];
				if (arrow.indexOf("n") != -1)
					options.mouseY -= options.arrowRotateSpeed;
				if (arrow.indexOf("e") != -1)
					options.mouseX += options.arrowRotateSpeed;
				if (arrow.indexOf("s") != -1)
					options.mouseY += options.arrowRotateSpeed;
				if (arrow.indexOf("w") != -1)
					options.mouseX -= options.arrowRotateSpeed;
			});

			/**
			* Event handler for mousemove on overlay, stores x and y coords in options object.
			*
			* @param {Object} e			This object points to the event object.
			*/
			$(obj.find(".roundabout-overlay")).mousemove(function(e) {

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
				options.mouseX -= obj.find(".roundabout-viewer-window").offset().left;
				options.mouseY -= obj.find(".roundabout-viewer-window").offset().top;
			});

			/**
			* Main draw loop which is executed every 50ms.
			*/
			obj.everyTime(50,function() {

				// If scale tiles
				if (options.drawScale == true) {
					options.tileWidth = parseInt(parseFloat(options.orgTileWidth) * options.scale);
					options.panWidth = options.nrOfTiles * options.tileWidth;
					options.panHeight = parseInt(parseFloat(options.orgPanHeight) * options.scale);
					options.maxAngleX = (parseFloat(options.screenCenterX + options.hotspotSize/2) / parseFloat(options.panWidth)) * 360;
					options.speed = parseFloat(options.orgSpeed) / parseFloat(options.scale);

					obj
						.roundaboutScaleTiles(options.scale, "a")
						.roundaboutScaleTiles(options.scale, "b");
					options.drawScale = false;
				}

				var prevAngle = options.angle;
				var prevHeight = options.height;

				// Update angle / height
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

					obj
						.roundaboutScaleTiles(animScale, options.currentTile)
						.roundaboutDrawTiles(options.currentTile, animScale)
						.roundaboutDrawTiles(options.otherTile, options.scale);
				} else {
					if (drawObjects == true) {
						obj.roundaboutDrawTiles (options.currentTile, options.scale);

						// Set compass
						if (options.drawMap) {
							obj
								.find(".roundabout-map-compass")
									.removeClass()
									.addClass("roundabout-map-compass")
									.addClass("roundabout-map-compass-" + ["n","ne","e","se","s","sw","w","nw"][parseInt((options.angle+22.5)%360/45)]);
						}
					}
				}

				// Check if map available
				if (options.drawMap) {

					// Draw hotspots
					var oHotspot;
					if (typeof(options.panoramas[options.currentId]) != "undefined") {
						if (((options.animFrame == -1) && (drawObjects == true)) || (options.animFrame == options.nrOfAnimFrames)) {

							for (var iCount = 0; iCount < options.panoramas[options.currentId].hotspots.length; iCount++) {
								oHotspot = options.panoramas[options.currentId].hotspots[iCount];

								// Check if left from center
								var fDifangle = (options.angle - oHotspot.x_angle + 360) % 360;
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
									$(hotspotobj).css ("top", parseInt(oHotspot.y_angle * parseFloat(options.panHeight)) - parseInt(options.height * (options.panHeight - options.screenHeight)) - options.hotspotSize / 2);
									$(hotspotobj).show();

								// Check if right from center
								} else if ((fDifangle <= 360) && (fDifangle > 360 - options.maxAngleX)) {

									var fFactor = (360 - fDifangle) / options.maxAngleX;
									$(hotspotobj).css ("left", options.screenCenterX + parseInt (fFactor * (options.screenCenterX + options.hotspotSize/2)) - options.hotspotSize / 2);
									$(hotspotobj).css ("top", parseInt(oHotspot.y_angle * parseFloat(options.panHeight)) - parseInt(options.height * (options.panHeight - options.screenHeight)) - options.hotspotSize / 2);
									$(hotspotobj).show();

								} else {

									// Hide hotspot
									$(hotspotobj).hide();
								}
							}
						}
					}
				}

				// Check if animation running
				if (options.animFrame != -1) {

					// If end of animation
					if (options.animFrame == options.nrOfAnimFrames) {

						// Hide current frame
						obj.find(".roundabout-tile-" + options.currentTile)
							.hide()
							.css({
								"opacity": 1,
								"z-index": 3
							});
						obj.find(".roundabout-tile-" + options.otherTile).css("z-index", 4);

						// Reset scale
						obj.roundaboutScaleTiles(options.scale, options.currentTile);

						var sTemp = options.currentTile;
						options.currentTile = options.otherTile;
						options.otherTile = sTemp;

						// End anim
						options.animFrame = -1;

					// Not the end of the animation
					} else
						options.animFrame++;
				}
			});
		});
	};

	/**
	* Scale the specified tiles.
	*
	* @param {Float} newScale	New scale factor.
 	* @param {String} tile		Specifies which tiles must be draw, can be either "a" or "b"
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutScaleTiles = function(newScale, tile) {
		var obj = $(this);
		var options = $(this).data("options");

		// Calc values
		var newHeight = parseInt(parseFloat(options.orgPanHeight) * newScale);

		// Cycle through matched elements
		return this.each(function() {

			// Get tiles
			$(".roundabout-tile-" + tile, obj).each(function(i) {

				// Set new scales
				$(this)
					.width(i == options.nrOfTiles - 1?parseInt(parseFloat(options.lastTileWidth) * newScale):parseInt(parseFloat(options.orgTileWidth) * newScale))
					.height(newHeight)
					.children("img")
						.width(parseInt((parseFloat(options.orgTileWidth) * newScale * 11) + (parseFloat(options.lastTileWidth) * newScale)))
						.height(newHeight)
						.css("left", parseInt(-1 * parseFloat(options.orgTileWidth * i) * newScale));
			});
		});
	};

	/**
	* Set the image of the specified tile.
	*
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutSetImage = function() {
		var options = $($(this).parents(".roundabout-wrapper").get(0)).data("options");

		// Loop through matched elements
		return this.each(function() {

			// Set image
			$(this).children("img").attr("src", options.panoramas[options.currentId].src);
		});
	};

	/**
	* Draw the specified tiles with the specified scale.
	*
 	* @param {String} tile		Specifies which tiles must be draw, can be either "a" or "b"
	* @param {Float} localScale	The scale of the tiles to be drawn.
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutDrawTiles = function(tile, localScale) {
		var obj = $(this);
		var options = obj.data("options");
		var tiles = obj.find(".roundabout-tile-" + tile);

		// Loop through matched elements
		return this.each(function() {

			// Calc width / height
			iLocalTileWidth = parseInt(parseFloat(options.orgTileWidth) * localScale);
			iLocalTileWidthLast = parseInt(parseFloat(options.lastTileWidth) * localScale);
			iLocalPanWidth = options.nrOfTiles * options.tileWidth;
			iLocalPanHeight = parseInt(parseFloat(options.orgPanHeight) * localScale);
			fLocalMaxAngleX = (parseFloat(options.screenCenterX + options.hotspotSize/2) / parseFloat(options.panWidth)) * 360;

			// Check if animation
			var bAnim = ((options.animFrame != -1) && (tile == options.currentTile))?true:false;
			var fAnimFactor = parseFloat(options.nrOfAnimFrames-options.animFrame)/options.nrOfAnimFrames;

			// Set local angle
			var fLocalAngle = options.angle;
			if (bAnim) {
				fLocalAngle -= (options.animAngle*(1-fAnimFactor));
			}

			// Draw center tile
			var iTile = parseInt(fLocalAngle/360*options.nrOfTiles);
			if (iTile > 11)
				iTile = 11;
			var fLocalAngle = fLocalAngle/360*options.nrOfTiles-iTile;
			var iX = options.screenCenterX - parseInt(fLocalAngle*iLocalTileWidth);
			var iY = parseInt((iLocalPanHeight-options.screenHeight)*-options.height);
			$(tiles[iTile])
				.css({
					"left": iX,
					"top": iY,
					"opacity": bAnim?fAnimFactor:1
				})
				.show();

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

				$(tiles[iCurTile])
					.css({
						"left": iCurX,
						"top": iY,
						"opacity": bAnim?fAnimFactor:1
					})
					.show();
			}
			var iRightTile = iCurTile;

			// Draw tiles left from current
			iCurX = iX;
			iCurTile = iTile;
			while (iCurX > iLocalTileWidth * -1) {
				if (iCurTile == 0) {
					iCurTile = options.nrOfTiles-1;
					iCurX -= iLocalTileWidthLast;
				} else {
					iCurTile--;
					iCurX -= iLocalTileWidth;
				}

				$(tiles[iCurTile])
					.css({
						"left": iCurX,
						"top": iY,
						"opacity": bAnim?fAnimFactor:1
					})
					.show();
			}

			// Hide the rest of the tiles
			while (iCurTile != iRightTile) {
				$(tiles[iCurTile]).hide();
				iCurTile += options.nrOfTiles - 1;
				iCurTile %= options.nrOfTiles;
			}
		});
	};

	/**
	* Get the current panorama data from the backend.
	*
	* @return {Object}			Returns a pointer to the current object.
	*/
	$.fn.roundaboutGetPanorama = function() {
		var obj = $(this);
		var options = obj.data("options");

		// Loop through matched elements
		return this.each(function() {

			// Check if maps available
			if (options.drawMap) {

				// Clear hotspots
				var overlay = obj
					.find(".roundabout-overlay")
					.empty();

				// Add hotspots
				$(options.panoramas[options.currentId].hotspots).each(function () {

					// Create div
					overlay.append(

						// Create hotspot div
						$(document.createElement("div"))
							.addClass("roundabout-hotspot")
							.data("target_image", this.target_image)
							.data("x_angle", this.x_angle)

							/**
							* Event handler for mousedown on hotspot, navigates to the next panorama.
							*
							* @param {Object} e			This object points to the event object.
							*/
							.mousedown(function(e) {

								// Hide all hotspots during anim
								$(".roundabout-hotspot", obj).hide();
								options.currentId = $(this).data("target_image");
								options.animFrame = 0;
								options.animAngle = (options.angle - parseFloat($(this).data("x_angle")) + 360) % 360;
								if (options.animAngle > 180)
									options.animAngle -= 360;
								obj
									.roundaboutGetPanorama()
									.find(".roundabout-tile-" + options.otherTile)
									.roundaboutSetImage();
							})
					);
				});

				// Show current map
				obj.find(".roundabout-map-container").children()
					.hide()
					.parent()
					.children("#roundabout-map-" + options.panoramas[options.currentId].map)
					.show();

				// Set compass
				obj.find(".roundabout-map-compass")
					.show()
					.css({
						left: options.panoramas[options.currentId].mapx - parseInt(options.compassSize/2),
						top: options.panoramas[options.currentId].mapy - parseInt(options.compassSize/2)
					});
			}
		});
	};
})(jQuery);
