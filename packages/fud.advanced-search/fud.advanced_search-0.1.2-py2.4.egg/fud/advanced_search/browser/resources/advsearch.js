jq(document).ready(function(){
   jq(".as-tooltip").hide();
   jq("a.as-field-tip").toggle(
   function(e){
       jq(".as-tooltip").hide();
       showTooltip(this.id+"div", e.pageX, e.pageY);
   },
   function(){
       jq("#"+this.id+"div").fadeOut(500);
   });

   jq("div.as-tooltip").click(function(){
      jq(this).fadeOut(500);
   });
});

function showTooltip(id,x,y){
   var h = jq("#"+id).height();
   jq("#"+id).css({"top":y-h-10,"left":x+20});
   jq("#"+id).hide().fadeIn(1000);
}
//function hideTooltip(id){
//    $("#"+id+"div").fadeOut(1000);
//}