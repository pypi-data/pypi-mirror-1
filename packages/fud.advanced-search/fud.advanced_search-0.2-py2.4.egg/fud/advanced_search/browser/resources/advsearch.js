jq(document).ready(function(){
   //jq(".as-tooltip").hide();
   ignore=false;
   tip=false;
   jq("a.as-field-tip").click(function(e){
       if(tip){
          jq(".as-tooltip").fadeOut(500);
          tip=false;
       }
       else{
           makeTooltip(this.id, e.pageX, e.pageY);
           ignore=true;
           tip=true;
       }
   });
   jq(".as-tabhead").click(
       function(){
       sortby=this.id;
       switch (sortby) {
            case 'as-tabhead-title':
                jq("#as-sort-selector").val("sortable_title");
                break;
            case 'as-tabhead-creator':
                jq("#as-sort-selector").val("Savedby");
                break;
            case 'as-tabhead-modified':
                jq("#as-sort-selector").val("modified");
                break;
            case 'as-tabhead-title-desc':
                jq("#as-sort-selector").val("sortable_title desc");
                break;
            case 'as-tabhead-creator-desc':
                jq("#as-sort-selector").val("Savedby desc");
                break;
            case 'as-tabhead-modified-desc':
                jq("#as-sort-selector").val("modified desc");
                break;
            default:
                break;
        }
       jq("#as-submit-form").click();}
   );
   //check if something on the screen was clicked
   //in case it is the tip(Hilfe) button, and the ignore is not set,
   //hide the
   jq("body").click(function(){
      if(ignore){
        ignore=false;
      }
      else{
        jq(".as-tooltip").fadeOut(500);
        tip=false;
      }
   });
   jq(".as-reset").click(function(){
       jq("#"+this.name).val("");
   })
   jq(".as-info-hl").toggle(
        function(){
            jq("#"+this.id).html("(-)");
            jq("."+this.id).show("slow");
        },
        function(){
            jq("#"+this.id).html("(+)");
            jq("."+this.id).slideUp("slow");
        }
     );
   jq(".as-hide-show a").toggle(
        function(){
            jq("#"+this.id).html("Form zeigen");
            jq("#as-search-form").slideUp();
        },
        function(){
            jq("#"+this.id).html("Form verstecken");
            jq("#as-search-form").show("slow");
        }
     );
});



function makeTooltip(id,x,y){
    msg="";
    switch (id) {
        case "as-tip1":
            msg = "<p><b>Alle</b> in diesem Feld stehende Wörter sollen im Text entahlten sein.<br />\
        Ein Leerzeichen trennt die Wörter aus einander. <br />z.B: Deutschland Wirtschaft Tendenz</p>"
            break;
        case "as-tip2":
            msg = "<p><b>Mindestens einer</b> der in diesem Feld stehende Wörter sollen im Text entahlten sein.<br />\
        Ein Leerzeichen trennt die Wörter aus einander. z.B: Deutschland Wirtschaft Tendenz</p>"
            break;
        case "as-tip3":
            msg = "<p>Der <b>aus mehreren Wörtern</b> bestehede Begriff soll im Text vollständig entahlten sein.<br />\
                       z.B: Fremdheit im Mittelalter</p>"
            break;
        case "as-tip4":
            msg = "<p><b>Keiner</b> der in diesem Feld stehende Wörter sollen im Text entahlten sein.<br />\
                                Ein Leerzeichen trennt die Wörter aus einander. z.B: Deutschland Wirtschaft Tendenz<br />\
                                Funktioniert nur wenn einer der oberen Feldern benutzt wurde.</p>"
            break;
        case "as-tip5":
            msg = "<p> Wählen Sie <b>eine oder mehrere Kategorien</b> für ihre Suche.<br />\
                    Um mehrere auszuwählen halten Sie sie Strg-taste(Ctrl) gedrückt<br /> und klicken Sie\
                    mit der Maustaste auf die gewünschte Kategorien.</p>"
            break;
        case "as-tip6":
            msg = "<p>Wählen Sie <b>eine/n oder mehrere Autoren</b> für ihre Suche.<br />\
                    Falls Sie ausschließlich eine Zusammenarbeit der gewünschten<br />\
                     Autoren auflisten möchten, markieren Sie die 'Kooperation' Kontrollkästchen.\
                     Um mehrere auszuwählen halten Sie sie Strg-taste (Ctrl) gedrückt und klicken Sie\
                     mit der Maustaste auf die gewünschte Kategorien.</p>"
            break;
        default:
            break;
    }
    jq("#in-tipdiv").html(msg);
    var h = jq("#as-tipdiv").height();
    jq("#as-tipdiv").css({"top":y-h-10,"left":x-30}).fadeIn(500);

}
//<img width="18" height="9" src="++resource++asresources/as-triang.png" alt="as-triang.png" />
//function hideTooltip(id){
//    $("#"+id+"div").fadeOut(1000);
//}