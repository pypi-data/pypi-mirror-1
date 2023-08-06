
function reload_slides(){
    //reloads the list of slides--just calls the widget info
    (function($){
    //begin $ namespace
    $.get($('input#slides-view-url').val(), {}, function(data, status){
        $('div#slides-view').html($(data).html());
        setup_events();
    });
    //end $ endspace
    })(jQuery);
}

function slide_click(){
    return (function($, ele){
    //begin $ namespace
    var overlay = $("<div class='slide-overlay'></div>");
    var wrapper = $("<div class='slide-modal'></div>");
    var finish_button = $(
        "<div class='finish-button'>" + 
            "<a href='' onclick='return false'>" + 
                "Click here when you are finished" +
            "</a>" +
            "<p class='discreet'>" +
                "Make sure you save first" + 
            "</p>" +
        "</div>"
    );
    var iframe = $(
        "<iframe src='" + $(ele).attr('href') + "' width='700' height='400' border='0'>" +
            "Your browser does not support iframes" +
        "</iframe>"
    );
        
    wrapper.append(iframe);
    wrapper.append(finish_button);
    
    $('body').append(overlay);
    $('body').append(wrapper);
    
    $('div.finish-button').click(function(){
        $('div.slide-overlay').remove();
        $('div.slide-modal').remove();
        reload_slides();
        return false;
    });         
    
    return false;
    //end $ namespace
    })(jQuery, this);
}

function setup_events(){
    //needs to be recalled whenever slides are retrieved
    (function($){
    //begin $ namespace
    function move_action(){
        //event for all move actions(up, down, delete)
        
        if($(this).hasClass('remove')){
            if(!window.confirm("Are you sure you want to remove this slide?")){
                return false;
            }
        }
        $.get($(this).attr('href') + '?ajax=true', {}, function(data, status){
            reload_slides();
        });
        return false;
    }

    $("div.slide-buttons a.move-up").click(move_action);
    $("div.slide-buttons a.move-down").click(move_action);
    $("div.slide-buttons a.remove").click(move_action);

    $("div.slide-buttons a.edit").click(slide_click);
    $("a.add-new").click(slide_click);
    //end $ namespace
    })(jQuery);
}

(function($){
    $(document).ready(function(){
        setup_events();//fire it up!
    });
})(jQuery);