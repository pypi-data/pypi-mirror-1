/* ==========================================================================
// jquery.panorama.js
// Author: Arnault PACHOT & Frédéric Martini
// Copyright (c) 2009 
// licence : GPL
// Patched for Plone integration: Maik Derstappen - Derstappen IT Consulting
============================================================================= */
(function(jq) {
    jq.fn.panorama = function(options) {
        this.each(function(){ 
            var settings = {
                viewport_width: 600,
                speed: 20000,
                direction: 'left',
                control_display: 'auto',
                start_position: 0,
                auto_start: true,
                mode_360: true,
                loop_180: true
            };
            if(options) jq.extend(settings, options);
            var elemWidth =  parseInt(jq(this).attr('width'));
            var elemHeight = parseInt(jq(this).attr('height'));
            // --------------------------------------------------
            // Récupération automatique de la taille de l'image :
            // Si un des attributs width ou height est absent, 
            // on récupère la vrai taille de l'image :
            if (isNaN(elemWidth) || isNaN(elemHeight)) {
                var img = new Image();
                img.src = jq(this).attr('src');
                if (isNaN(elemWidth)) elemWidth = img.width;
                if (isNaN(elemHeight)) elemHeight = img.height;
            }
            // --------------------------------------------------
            var currentElement = this;
            var panoramaViewport, panoramaContainer;
            jq(this).css('position', 'relative')
                .css('margin', '0')
                .css('padding', '0')
                .css('border', 'none')
                .wrap("<div class='panorama-container'></div>");
            jq(this).css('display', 'inline-block');
            if (settings.mode_360) 
                jq(this).clone().insertAfter(this);

            panoramaContainer = jq(this).parent();
            panoramaContainer.wrap("<div class='panorama-viewport'></div>").parent().css('width',settings.viewport_width+'px')
                .append("<div class='panorama-control'><a href='#' class='panorama-control-left'><<</a> <a href='#' class='panorama-control-pause'>x</a> <a href='#' class='panorama-control-right'>>></a> </div>");

            panoramaViewport = panoramaContainer.parent();
            panoramaViewport.css('height', elemHeight+'px').find('a.panorama-control-left').bind('click', function() {
                jq(panoramaContainer).stop();
                settings.direction = 'right';
                panorama_animate(panoramaContainer, elemWidth, settings);
                return false;
            });
            panoramaViewport.bind('click', function() {
                jq(panoramaContainer).stop();
            });
            panoramaViewport.find('a.panorama-control-right').bind('click', function() {
                jq(panoramaContainer).stop();
                settings.direction = 'left';
                panorama_animate(panoramaContainer, elemWidth, settings);
                return false;
            });
            panoramaViewport.find('a.panorama-control-pause').bind('click', function() {
                jq(panoramaContainer).stop();
                return false;
            });

            if (settings.control_display == 'yes') {
                panoramaViewport.find('.panorama-control').show();
            } else if (settings.control_display == 'no') {
                panoramaViewport.find('.panorama-control').hide();
            } 
            else {
                panoramaViewport.bind('mouseover', function(){
                    jq(this).find('.panorama-control').show();
                    return false;
                }).bind('mouseout', function(){
                    jq(this).find('.panorama-control').hide();
                    return false;
                });
            }
            jq(this).parent().css('margin-left', '-'+settings.start_position+'px');
            if (settings.auto_start) 
                panorama_animate(panoramaContainer, elemWidth, settings);
        });
        function panorama_animate(element, elemWidth, settings) {
            currentPosition = 0-parseInt(jq(element).css('margin-left'));
            if (settings.direction == 'right') {
                jq(element).animate({marginLeft: 0}, ((settings.speed / elemWidth) * (currentPosition)) , 'linear', function (){ 
                    if (settings.mode_360) {
                        jq(element).css('marginLeft', '-'+(parseInt(parseInt(elemWidth))+'px'));
                        panorama_animate(element, elemWidth, settings);
                    } else if (settings.loop_180) {
                        settings.direction = 'left'; // changement de sens 
                        panorama_animate(element, elemWidth, settings);
                    }
                });
            } else {
                var rightlimit;
                if (settings.mode_360) 
                    rightlimit = elemWidth;
                else
                    rightlimit = elemWidth-settings.viewport_width;
                jq(element).animate({marginLeft: -rightlimit}, ((settings.speed / rightlimit) * (rightlimit - currentPosition)), 'linear', function (){ 
                    if (settings.mode_360) {
                        jq(element).css('margin-left', 0); 
                        panorama_animate(element, elemWidth, settings);
                    } else if (settings.loop_180) {
                        settings.direction = 'right'; // changement de sens
                        panorama_animate(element, elemWidth, settings);
                    }
                });
            }
        }
    };



/*jq(document).ready(function(){
    jq("img.panorama").panorama({
                 viewport_width: 760,
                 speed: 30000,
                 mode_360: false
         });
});*/
})(jQuery);

