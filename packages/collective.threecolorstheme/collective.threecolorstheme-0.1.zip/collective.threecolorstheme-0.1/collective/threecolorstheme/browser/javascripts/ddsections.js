var ua = navigator.userAgent;
var isIE6 = (ua.match(/MSIE 6\.0/)); 
var isIE = jQuery.browser.msie

fixSubmenuPos = function(elt) {
    /* fix position of submenu at item height -1px */
    mt = jQuery(elt);
    mth = mt.height();
    mtclass = mt.attr("class");
    isSubitem = mtclass.match(/subitem/);
    menu= jQuery("ul.submenu", mt);
    if (isSubitem && menu.length) {        
        if (isIE6) {
            newtoppoz = 5-mth+30;
        }
        else {
            newtoppoz = 5-mth;
        }
        menu.css("top", newtoppoz + "px");   
    }
}


jQuery.fn.extend({
    findPos : function() {
        obj = $(this).get(0);
        var curleft = obj.offsetLeft || 0;
        var curtop = obj.offsetTop || 0;
        while (obj = obj.offsetParent) {
            curleft += obj.offsetLeft
            curtop += obj.offsetTop
        }
        return {x:curleft,y:curtop};
    }
});

var CONTENT_HAS_BAD_SELECTLISTS = false;

ContentHasBadSelectLists = function() {
    if (isIE6) {
        var selectLists = jQuery('#portal-columns select');
        if (selectLists.length) {
            CONTENT_HAS_BAD_SELECTLISTS = true;
        }    
    }
}

jQuery(document).ready(ContentHasBadSelectLists);

createMaskFor = function(obj) {
    if (jQuery.browser.msie) {
        var menu = jQuery("ul", obj);
        if (menu.length) {
            menuWidth = menu.width()+2;
            menuHeight = menu.height()+2;
            menuPos = menu.findPos();
            /* create the iframe mask if not exists */
            idMask = "mask-for-" + obj.id;
            if (jQuery('#'+idMask).length==0) {        
                jQuery("#visual-portal-wrapper").append('<iframe id="' + idMask + '" class="iframeMask" src="about:blank"></iframe>');
            }              
            /* fix position and dimensions */
            mask = jQuery('#'+idMask);  
            mask.css({ top : (menuPos.y-1)+"px", 
                       left : (menuPos.x-1)+"px", 
                       width: menuWidth+"px", 
                       height: menuHeight+"px"});                
        }
    }   
}

showMaskFor = function (obj) {
    if (jQuery.browser.msie) {
        var menu = jQuery("ul", obj);
        if (menu.length) {
            idMask = "mask-for-" + obj.id;
            mask = jQuery('#'+idMask);    
            hoverClass = obj.className ;
            isActive = hoverClass.match(/sfhover/);
            if (isActive) {
                mask.addClass('iframeMaskActive');     
                mask.css({ display: "block", zIndex: "10" });         
            } 
        }
    }   
}


hideMaskFor = function(idObj) {
    if (jQuery.browser.msie) {
        obj= document.getElementById(idObj);
        if (obj) {
            hoverClass = obj.className ;
            isActive = hoverClass.match(/sfhover/);
            if (!isActive) {    
                mask = jQuery('#mask-for-' + idObj);
                mask.removeClass('iframeMaskActive');
                mask.css({ display: "none", zIndex: "-1" }); 
            }
        }
    }
}



makeHoverClasses = function(elt) {
	jQuery(elt).hover(
      function() {
          jQuery(this).addClass('sfhover');
          // simulate hover on first link child (for skin reason)
          jQuery('a.niv1link', this).addClass('slHover');
          fixSubmenuPos(this);
          // fix IE6/IE7 z-index bugs with relative positionned objects
          // remove position relative hack for IE
          if (isIE) {
              jQuery('dl.actionMenu').css('position', 'static');
              jQuery('ul.contentViews').css('position', 'static');
              jQuery('div.contentActions').css('position', 'static');
              jQuery('ul.formTabs').css('position', 'static');
              jQuery('fieldset.formPanel').css('border-style', 'none');
              jQuery('#searchForm fieldset').css('border-style', 'none');
          }    
          if (CONTENT_HAS_BAD_SELECTLISTS) {
              showMaskFor(this);         
          }
      },
      function() {
      		jQuery(this).removeClass('sfhover');
          // remove hover simulation on first link child
          jQuery('a.niv1link', this).removeClass('slHover');
          // restore position relative hack for IE
          if (isIE) {
              jQuery('dl.actionMenu').css('position', 'relative');
              jQuery('ul.contentViews').css('position', 'relative');
              jQuery('div.contentActions').css('position', 'relative');
              jQuery('ul.formTabs').css('position', 'relative');
              jQuery('fieldset.formPanel').css('border-style', 'solid');
              jQuery('#searchForm fieldset').css('border-style', 'solid');
          }    
          if (CONTENT_HAS_BAD_SELECTLISTS) {  
              hideMaskFor(this.id) ;
          }
      }
  );  
}

sfHover = function() {
    jQuery("#portal-globalnav li").each(function(){
         makeHoverClasses(this);
         if (CONTENT_HAS_BAD_SELECTLISTS) {
             createMaskFor(this);
         }    
    })   
}


/* selected tab done in javascript */

highlightSelectedTab = function()  {
    var selectedId = jQuery("#portal-globalnav #ddmenus_selectedid").val();
    var selectedTabId = 'portaltab-' + selectedId;
    var selectedTab = jQuery('#portal-globalnav #' + selectedTabId );
    if (selectedTab.length) {
        selectedTab.addClass('selected');
        jQuery('a', selectedTab[0] ).addClass('selected'); 
    }    
} 

 
//jQuery(document).ready(sfHover);

/* change body style depending on section's number mouseover
   or link selected.
   Really cool , don't care no more about section id in templates */
   
changeBodyClassOnSectionChange = function()  {
    jQuery('#portal-globalnav li.sectionniv1').each(function(i,link) { 
        var sectionNumber = i+1;        
        if (jQuery('a.selected', this).length) {
            jQuery('body').attr("id","section-nb" + sectionNumber);            
        }        
    });  
} 


initializeMenus = function() {
  var container = jQuery('#portal-globalnav');
  var urlmenu = jQuery('#ddmenus_ajaxurl', container[0]).val();
  jQuery.get(urlmenu,
      function(data){
        container.append(data); 
        jQuery(document).ready(sfHover);
        jQuery(document).ready(highlightSelectedTab);
        jQuery(document).ready(changeBodyClassOnSectionChange);
      }
  );
}

jQuery(document).ready(initializeMenus);


