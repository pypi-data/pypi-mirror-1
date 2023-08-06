/* FANCYBOX */

jq(document).ready(function () {
    jq("img[rel]").overlay(/*{
        'absolute':false,
        'speed':'fast',
        'top':-20,
        'left':-20
    }*/);
});


/* GALLERY */

jq(document).ready(function () {
    jq("div.scrollable").scrollable();
    
    jq("div.galleryItems img").click(function() { 

        // calclulate large image's URL based on the thumbnail URL (flickr specific)
        imgel = jq(this)
        var url = imgel.attr("src").replace("_thumb", "_preview");
        var url_full = imgel.attr("src").replace("_thumb", "_view_fullscreen");
        var title = imgel.attr("alt");
        var desc = imgel.attr("title");

        // get handle to element that wraps the image and make it semitransparent 
        var wrap = jq("#image_wrap").fadeTo("medium", 0.5); 

        // the large image from flickr 
        var img = new Image(); 

        // call this function after it's loaded 
        img.onload = function() {

            // make wrapper fully visible 
            wrap.fadeTo("fast", 1); 

            // change the image 
            wrap.find("img").attr("src", url); 

        }; 

        img.src = url;
        var img_link = jq("div.imageTitle a");
        img_link.html(title);
        img_link.attr("href", url_full);
        img_link.attr("title", desc);

    // when page loads simulate a "click" on the first image 
    }).filter(":first").click();
    
});
