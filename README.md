# webcamlocation
This is an experiment to do geolocation of webcameras using light levels. See [the wikipedia page](https://en.wikipedia.org/wiki/Light_level_geolocator) on light-level geolocation. 

### usage
To use the tool, navigate to [the app landing page](http://webcamlocation.appspot.com) and input a webcamera url. This should be the naked webcamera feed like `http://playdogplay.viewmydog.com/cam10.jpg`

![doggy cam](http://playdogplay.viewmydog.com/cam10.jpg)

We can handle "streaming" jpegs too. After submitting, you'll be shown a message telling you to check back in twentyfour hours. While you wait, we'll check the relative light level in the webcam feed every five minutes. After one day has passed you should be able to see a complete light level curve, like the one before


![graph](http://i.imgur.com/WKH13Xn.png)

Click the sunrise button then click on the location of the graph where the light level indicates sunrise. Click sunset and then click the location on the graph where the light level indicates sunset. After setting both the sunrise and sunset points, you should see a map with the approximate location, like the map below

![map](http://i.imgur.com/cGaPVzv.jpg)

If you move the sunrise/sunset locations, the map should update with the new location estimate. In this case its only ~100 miles off. Not bad!
