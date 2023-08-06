
/* change some labels with no translation  */

changeSomeLabels = function(){
    jQuery('#portal-searchbox .searchButton').each(function(){jQuery(this).val('>>')});
}
jQuery(document).ready(changeSomeLabels);


/* we always want a special class for column-content when there are no columns one or two */

changeContentColumnClass = function(){
    var col1 = jQuery('#portal-column-one');
    var col2 = jQuery('#portal-column-two');   
    var colcenter = jQuery('#portal-column-content'); 
    if (! col1.length) {
        colcenter.addClass('contentColumnWithNoLeft');
    }
    if (! col2.length) {
        colcenter.addClass('contentColumnWithNoRight');
    }    
}
jQuery(document).ready(changeContentColumnClass);