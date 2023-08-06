sylvester = {}

/* Set a cookie which stores the browser's timezone */
/* Not used currently */
sylvester.setupCookie = function(){
    var name = 'collective.sylvester.timezoneoffset';
    var expiredays = 7;
    var found = false;
    if (document.cookie.length > 0)
    {
        if (document.cookie.indexOf(name + "=") != -1)
            found = true;        
    }    

    if (!found)
    {
        var exdate = new Date();
        exdate.setDate(exdate.getDate() + expiredays);
        document.cookie = name + "=" + escape(exdate.getTimezoneOffset()) +
            ((expiredays == null) ? "" : ";expires=" + exdate.toGMTString());
    }
};

sylvester.rollover = function(sender){
    jq(sender).toggleClass("collective-sylvester-statuses-highlight");
};

sylvester.onUpdateKeyUp = function(sender){
    var len = parseInt(sender.value.length);
    var remaining = 140 - len;

    if (remaining <= 0)    
    {
        sender.value = sender.value.substring(0, 140);
        remaining = 0;
    }

    var div = document.getElementById('collective-sylvester-characters-remaining');
    div.innerHTML = remaining;
};

sylvester.prepareReply = function(username){
    jq('#collective-sylvester-dashboard-tweet-form textarea').text('@'+username+' ').focus();
};
