var kssmessages = {};

kssmessages.popupShow = function(msg)
{  
    // Return if popup is already visible. We only want the user to
    // deal with one error at a time.  
    var popup = document.getElementById('kssmessages-popup');
    if (popup.className == 'kssmessages-popup-visible')
        return;

    var popup_message = document.getElementById('kssmessages-popup-message');
    popup_message.innerHTML = msg;
    popup.className = 'kssmessages-popup-visible';
    jq('#kssmessages-popup').vCenter();
};

kssmessages.popupHide = function()
{
    var popup = document.getElementById('kssmessages-popup');
    popup.className = 'kssmessages-popup-hidden';
    var popup_message = document.getElementById('kssmessages-popup-message');
    popup_message.innerHTML = '';
};

// Register function with jQuery
// todo: find a nicer way to do this
// Maybe someday standard jQuery will have an equivalent function and
// I can get rid of this one.
(function($){
  $.fn.vCenter = function(options) {
    var pos = {
    sTop : function() {
      return window.pageYOffset
      || document.documentElement && document.documentElement.scrollTop
      ||    document.body.scrollTop;
    },
    wHeight : function() {
      return window.innerHeight
      || document.documentElement && document.documentElement.clientHeight
      || document.body.clientHeight;
    },
    sLeft : function() {
      return window.pageXOffset
      || document.documentElement && document.documentElement.scrollLeft
      ||    document.body.scrollLeft;
    },
    wWidth : function() {
      return window.innerWidth
      || document.documentElement && document.documentElement.clientWidth
      || document.body.clientWidth;
    }
    };
    return this.each(function(index) {
      if (index == 0) {
        var $this = $(this);
        var elHeight = $this.height();
        var elWidth = $this.width();
        var elTop = pos.sTop() + (pos.wHeight() / 2) - (elHeight / 2);
        var elLeft = pos.sLeft() + (pos.wWidth() / 2) - (elWidth / 2);
        if (elTop < 10)
            elTop = 10;
        $this.css({
          position: 'absolute',
          marginTop: '0',
          top: elTop,
          left: elLeft
        });
      }
    });
  }; 
})(jQuery);
