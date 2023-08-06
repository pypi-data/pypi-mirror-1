collective.contentleadimage Package Readme
==========================================

Overview
--------

This products adds complete support for adding descriptive image to any
Archetypes based content in Plone site. Each object has new tab "Edit lead
image", which allows to upload new or remove current image. It is similar
behaviour as Plone News Item (you can add image to news item and this image is
displayed in news item overview listing.

There is folder_leadimage_view page template, which can be used to list all
items in the folder together with images attached.

There is configuration control panel, where you can set maximum width and height
of the uploaded images. The widht and height is applied on each image upload
(image is automatically resized). You can specify smaller width and height 
which is used as image preview in the below content title viewlet (next to 
content Description). Large image is used in the above content body viewlet
(floated left at the top of content body). 

Below content title viewlet is preffered, but Manager can easily switch
the viewlets on/off in the control panel.

There is FieldIndex and metadata in portal_catalog: hasContentLeadImage
(True/False). This may help developers to create own templates optimized 
for displaying lead image.

