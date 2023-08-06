collective.roundabout
=====================

This product lets you add 360 degree panoramic photos to your website by tagging
your image in the WYSIWYG editor (TinyMCE and Kupu supported). The image will be
tagged with the "roundabout" class which is converted into a viewer using
jQuery when the page is displayed. The viewer is javascript only, so plugins
like flash are not needed.

This product also has a couple of contenttypes which you can use to create a
virtual tour of multiple panoramic photos. This tour includes one (or more)
overview maps and a compass at the current location.


Test Setup
----------

In order to test the tour let's setup a simple tour. First we'll add the Manager
role so we can add the RoundAbout content types to the portal root.

    >>> self.setRoles(['Manager'])

Next we'll create a basic tour object called 'testtour'.

    >>> self.folder.invokeFactory('RoundAbout Tour', id='testtour', title='Test Tour')
    'testtour'

We'll create a tour with two maps called 'firstfloor' and 'secondfloor'.

    >>> tour = self.folder['testtour']

    >>> tour.invokeFactory('RoundAbout Map', id='firstfloor', title='First Floor')
    'firstfloor'

    >>> tour.invokeFactory('RoundAbout Map', id='secondfloor', title='Second Floor')
    'secondfloor'

We should now have two maps

    >>> sorted(tour.objectIds())
    ['firstfloor', 'secondfloor']

Let's add some images to those map objects. We'll get the image data first.

    >>> import os
    >>> current_file = globals()['__file__']
    >>> test_image, _ = os.path.split(current_file)
    >>> test_image = os.path.join(test_image, 'browser')
    >>> test_image = os.path.join(test_image, 'images')
    >>> test_image = os.path.join(test_image, 'hotspot.gif')
    >>> raw_image = open(test_image, 'rb').read()

Now let's put that data in the map objects.

    >>> field = tour.firstfloor.getField('image')
    >>> field.set(tour.firstfloor, raw_image)
    >>> field = tour.secondfloor.getField('image')
    >>> field.set(tour.secondfloor, raw_image)

Both these maps will have hotspots so you can navigate from one map to another.
Hotspots are specified with the x and y coordinate of the top left corner of the
hotspot (measured from the top left corner of the image), the width, the height
and the target map of the hotspot. Let's create one hotspot on each map.

    >>> tour.firstfloor.invokeFactory('RoundAbout Map Hotspot',
    ...     id='tothesecondfloor',
    ...     title='To the Second Floor',
    ...     target_map='secondfloor',
    ...     x=50,
    ...     y=10,
    ...     width=20,
    ...     height=20)
    'tothesecondfloor'

    >>> tour.secondfloor.invokeFactory('RoundAbout Map Hotspot',
    ...     id='tothefirstfloor',
    ...     title='To the First Floor',
    ...     target_map='firstfloor',
    ...     x=50,
    ...     y=10,
    ...     width=20,
    ...     height=20)
    'tothefirstfloor'

Next up are the panoramic images. We'll create two, one for each floor. An
panoramic image contains the name of map on which it is located and the x and y
coordinate on that map. Let's create two images.

    >>> tour.invokeFactory('RoundAbout Image',
    ...     id='image1',
    ...     title='Image1',
    ...     image=raw_image,
    ...     map='firstfloor',
    ...     mapx=30,
    ...     mapy=40)
    'image1'

    >>> tour.invokeFactory('RoundAbout Image',
    ...     id='image2',
    ...     title='Image2',
    ...     image=raw_image,
    ...     map='secondfloor',
    ...     mapx=50,
    ...     mapy=60)
    'image2'

Our tour should now contain two maps and two images

    >>> sorted(tour.objectIds())
    ['firstfloor', 'image1', 'image2', 'secondfloor']

Images can also contain hotspots. These hotspots are placed on the images so you
can navigate from one image to anoter. Hotspots are defined by an x and a y
angle. The x angle is between 0 and 360 degrees. The y angle is between 0 and 1
where 0 is below and 1 above. The hotspots also has a property for the target
image. Let's create two hotspots, one for each image.

    >>> tour.image1.invokeFactory('RoundAbout Image Hotspot',
    ...     id='toimage2',
    ...     title='To Image 2',
    ...     target_image='image2',
    ...     x_angle=180,
    ...     y=0.5)
    'toimage2'

    >>> tour.image2.invokeFactory('RoundAbout Image Hotspot',
    ...     id='toimage1',
    ...     title='To Image 1',
    ...     target_image='image1',
    ...     x_angle=90,
    ...     y=0.75)
    'toimage1'

In the tour object we can specify some configuration options for the viewer.
First we'll set the viewer width and height.

    >>> tour.viewer_width = 400
    >>> tour.viewer_height = 300

Next we can specify the start image and the start angle of that image.

    >>> tour.start_image = 'image1'
    >>> tour.start_angle = 270

And finaly the number of frames in the animation between two panoramic images

    >>> tour.animation_frames = 20


Browser Views
-------------

Our tour is now complete. Let's see if our browser views return the correct
values. First we'll setup a browser.

    >>> from collective.roundabout.browser.browser import roundabouttour_view
    >>> view = roundabouttour_view(tour, None)

The configuration data is all the data which is needed to let the client draw
the viewer. It is returned in JSON and should look like the structure below.

    >>> view.getViewerData()
    "{'viewer_width':'400','viewer_height':'300','start_image':'image1','start_angle':'270','animation_frames':'20'}"

Next we'll test the getImages method. This method should return a list of all
the images with all the attributes.

    >>> view.getImages()
    [{'title': 'Image1', 'url': 'http://nohost/plone/Members/test_user_1_/testtour/image1/image', 'height': '28', 'width': '28', 'data': u"{'id':'image1','map':'firstfloor','mapx':'30','mapy':'40','hotspots':[{'target_image':'image2','x_angle':'180.0','y_angle':'None'}]}", 'id': 'image1'}, {'title': 'Image2', 'url': 'http://nohost/plone/Members/test_user_1_/testtour/image2/image', 'height': '28', 'width': '28', 'data': u"{'id':'image2','map':'secondfloor','mapx':'50','mapy':'60','hotspots':[{'target_image':'image1','x_angle':'90.0','y_angle':'None'}]}", 'id': 'image2'}]

Next we'll test the getMaps method. This method should return a list of all
the maps with all the attributes.

    >>> view.getMaps()
    [{'title': 'First Floor', 'url': 'http://nohost/plone/Members/test_user_1_/testtour/firstfloor/image', 'height': '28', 'width': '28', 'data': u"{'id':'firstfloor','hotspots':[{'target_map':'secondfloor','x':50,'y':10,'width':20,'height':20}]}", 'id': 'firstfloor'}, {'title': 'Second Floor', 'url': 'http://nohost/plone/Members/test_user_1_/testtour/secondfloor/image', 'height': '28', 'width': '28', 'data': u"{'id':'secondfloor','hotspots':[{'target_map':'firstfloor','x':50,'y':10,'width':20,'height':20}]}", 'id': 'secondfloor'}]
