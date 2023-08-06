from Products.Five import BrowserView
from Acquisition import aq_inner

class roundabouttour_view(BrowserView):

	def getImages(self):
		catalog_results = []

		object = aq_inner(self.context)

		for brain in object.getFolderContents({'portal_type': 'RoundAbout Image', 'sort_on': 'sortable_title'}):
			image = brain.getObject()
			data = "'id':'%s','map':'%s','mapx':'%s','mapy':'%s'" % (image.getId(), image.map, image.mapx, image.mapy)
			hotspots = []
			for image_brain in image.getFolderContents({'portal_type': 'RoundAbout Image Hotspot', 'sort_on': 'sortable_title'}):
				hotspot = image_brain.getObject()
				hotspots.append("{'target_image':'%s','x_angle':'%s','y_angle':'%s'}" % (hotspot.target_image, hotspot.x_angle, hotspot.y_angle))
			catalog_results.append({
				'id': brain.getId,
				'title': brain.Title,
				'url': "%s/image" % brain.getURL(),
				'width': "%s" % image.get('image').width,
				'height': "%s" % image.get('image').height,
				'data': "{%s,'hotspots':[%s]}" % (data, ','.join(hotspots))
			})

		return catalog_results

	def getMaps(self):
		catalog_results = []

		object = aq_inner(self.context)

		for brain in object.getFolderContents({'portal_type': 'RoundAbout Map', 'sort_on': 'sortable_title'}):
			map = brain.getObject()
			data = "'id':'%s'" % map.getId()
			hotspots = []
			for map_brain in map.getFolderContents({'portal_type': 'RoundAbout Map Hotspot', 'sort_on': 'sortable_title'}):
				hotspot = map_brain.getObject()
				hotspots.append("{'target_map':'%s','x':%s,'y':%s,'width':%s,'height':%s}" % (hotspot.target_map, hotspot.x, hotspot.y, hotspot.width, hotspot.height))
			catalog_results.append({
				'id': brain.getId,
				'title': brain.Title,
				'url': "%s/image" % brain.getURL(),
				'width': "%s" % map.get('image').width,
				'height': "%s" % map.get('image').height,
				'data': "{%s,'hotspots':[%s]}" % (data, ','.join(hotspots))
			})

		return catalog_results

	def getViewerData(self):
		catalog_results = []

		object = aq_inner(self.context)

		return "{'viewer_width':'%s','viewer_height':'%s','start_image':'%s','start_angle':'%s','animation_frames':'%s'}" % (
			object.get('viewer_width'),
			object.get('viewer_height'),
			object.get('start_image'),
			object.get('start_angle'),
			object.get('animation_frames'))
