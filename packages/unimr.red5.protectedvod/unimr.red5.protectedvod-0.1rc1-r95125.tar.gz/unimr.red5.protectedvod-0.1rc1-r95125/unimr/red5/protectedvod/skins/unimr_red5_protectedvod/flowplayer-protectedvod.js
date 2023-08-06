jq.preloadImages = function() {
    var a = (typeof arguments[0] == 'object')? arguments[0] : arguments;
    for(var i = a.length -1; i > 0; i--) {
	jq("<img>").attr("src", a[i]);
    }
};

var preload = ['nosplashimage.jpg', 'play-button.png'];
jq.preloadImages(preload);

jq(document).ready(function(){
	jq('div.red5-stream > a').each(function() {
		/* replace marked links with players */

		var width = 320;
		var height = 240;
		var background = 'nosplashimage.jpg';
		var autoPlay = true;
		
		var image = jq("img:only-child",this);
		var parent = jq(this).parent();

		if(image[0]){
		    var img = image[0];
		    parent.html(img);
		}  else {
		    var img = new Image();
		    img.src = background;
		    parent.html(img);
		}

		iwidth = img.width;
		width = (iwidth > 100) ?  iwidth : width;
		iheight = img.height;
		height = (iwidth > 100) ?  iheight : height;

		var cssObj = {
		    'width' : width + 'px',
		    'min-height' : height + 'px',
		    'max-height' : height + 'px',
		    'height' : 'auto !important',
                    'height' : height + 'px',
		    'display': 'block'
		};
		
		parent.css(cssObj);
		
		var position = parent.position();

		/* insert play button as overlay */
		var button = new Image();
		button.src = 'play-button.png';

		jq(parent).append('<div class="red5-stream-button"/>');
		var divButton = jq('div.red5-stream-button',parent).html(button);

		var top_pos  = position.top  + (height - button.height)/2.;
		var left_pos = position.left + (width - button.width)/2.;

		var cssObj = {
		    'position' : 'absolute',
		    'top' : top_pos+'px',
		    'left': left_pos+'px',
		    'height' : button.height,
		    'width' : button.width
		    
		};

		divButton.css(cssObj);	
		divButton.html(button);

		/* set the xml clip info (url, signature, etc.) */
		var info_url = this.href + '/protectedvod-info.xml';
		/* reset clip url */
		this.href="";

		/* embed flowplayer */
		jq(parent).flowplayer('flowplayer-3.1.2.swf', {
			/*
			debug: true ,
			log: { level: 'debug',
			       filter : 'org.flowplayer.rtmp.*'
			},
			*/
			clip: {scaling: 'fit',                      
			       provider: 'rtmp'
			},
			    
			plugins: {rtmp: {url: 'flowplayer.rtmp-3.1.1.swf'}
			    
			},
			
			onBeforeClick: function(){
			    var clip_url = '';
			    var clip_netConnectionUrl = '';
			    jq.ajax({ type: "GET",
					async: false,
					url:   info_url,
					dataType: "xml",  
					success: function(xml){
					jq(xml).find('clip').each(function(){
						clip_url = jq(this).text();
					    });
					jq('netConnectionUrl',xml).each(function(){
						clip_netConnectionUrl = jq(this).text();
					    });
				    }
				}); 
			    
			    this.play([{ url: clip_url,
                                         baseUrl: clip_netConnectionUrl
                                      }]);
			    
			    return true;

			}
			    
	        });
	    });
	
    });
