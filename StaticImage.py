import urllib
import cStringIO 
#from PIL import Image, ImageTk


def get_static_google_map(filename_wo_extension, center=None, zoom=16, imgsize=(500,500), imgformat="jpeg",
                          maptype="roadmap", markers=None ):  
    """retrieve a map (image) from the static google maps server 
    
     See: http://code.google.com/apis/maps/documentation/staticmaps/
        
        Creates a request string with a URL like this:
        http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512&maptype=roadmap&markers=color:blue|label:S|40.702147,-74.015794&sensor=false"""
   
    
    # assemble the URL
    request =  "http://maps.google.com/maps/api/staticmap?" # base URL, append query params, separated by &
   
    # if center and zoom  are not given, the map will show all marker locations
    if center != None:
        request += "center=%s&" % center
        #request += "center=%s&" % "40.714728, -73.998672"   # latitude and longitude (up to 6-digits)
        #request += "center=%s&" % "50011" # could also be a zipcode,
        #request += "center=%s&" % "Brooklyn+Bridge,New+York,NY"  # or a search term 
    if center != None:
        request += "zoom=%i&" % zoom  # zoom 0 (all of the world scale ) to 22 (single buildings scale)

	for i in imgsize:
		if i > 640:
			i = 640
	
    request += "size=%ix%i&" % (imgsize)  # tuple of ints, up to 640 by 640
    request += "format=%s&" % imgformat
    request += "maptype=%s&" % maptype  # roadmap, satellite, hybrid, terrain


    # add markers (location and style)
    if markers != None:
        for marker in markers:
                request += "%s&" % marker


    #request += "mobile=false&"  # optional: mobile=true will assume the image is shown on a small screen (mobile device)
    request += "sensor=false&"   # must be given, deals with getting loction from mobile device 
    #print request
    
    #urllib.urlretrieve(request, filename_wo_extension+"."+imgformat) # Option 1: save image directly to disk
    
    # Option 2: read into PIL 
    web_sock = urllib.urlopen(request)
    imgdata = cStringIO.StringIO(web_sock.read()) # constructs a StringIO holding the image
    try:
        return imgdata
		#PIL_img = PIL.Image.open(imgdata)
    
    # if this cannot be read as image that, it's probably an error from the server,
    except IOError:
        print "IOError:", imgdata.read() # print error (or it may return a image showing the error"
        return None
     
    # show image 
    else:
		return None
    #    PIL_img.show()
        #PIL_img.save(filename_wo_extension+".jpg", "JPEG") # save as jpeg