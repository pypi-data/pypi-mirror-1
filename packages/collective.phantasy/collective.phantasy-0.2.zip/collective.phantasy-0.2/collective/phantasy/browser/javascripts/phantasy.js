movePhantasyStyleAtBottom = function() {    
    var stylessheets = jQuery('head .phantasycssstylesheet');
    stylessheets.each(function(i){
      jQuery(this).insertAfter("head style");
      jQuery(this).remove();
    });;
}


jQuery(document).ready(movePhantasyStyleAtBottom);
