if (/3[\.0-9]+ Safari/.test(navigator.appVersion))
{
      window.console = {
          origConsole: window.console,
          log: function(s){
              this.origConsole.log(s);
          },
          info: function(s){
              this.origConsole.info(s);
          },
          error: function(s){
              this.origConsole.error(s);
          },
          warn: function(s){
              this.origConsole.warn(s);
          }
      };
}
  
dojo.require("dijit.dijit");
dojo.require("dijit.layout.BorderContainer");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.layout.AccordionContainer");
dojo.require("dijit.form.DateTextBox");
dojo.require("dijit.form.Form");
dojo.require("dijit.Dialog");
dojo.require("dojo.io.iframe");
dojo.require("dojo.html");
dojo.require("dojo.parser");
function sendIt(target, result){
    if(!result){
        result = 'content_pane';
    }
    dojo.io.iframe.send({
        form: dojo.byId(target),
        handleAs: "html",
        handle: function(response, ioArgs){
            if(response instanceof Error){
                console.log("Request FAILED: ", response);
            }else{
                var content_pane = dijit.byId(result);
                if(content_pane){
                    content_pane.attr('content', response.body.innerHTML);
                    console.log("Request complete: ", response);
                } else {
                    console.log('could not find ' + content_pane);
                }
            }
        }
    });
}

function viewIt(url){
    var content_pane = dijit.byId('content_pane');
    if (content_pane){
        content_pane.attr('href',url);
    } else{
        console.debug('could not find content_pane');
    }
}

function startIt(url){
    var dlog = dijit.byId('start_dlog');
    dlog.attr('href',url);
    dlog.show();
}

var view_date = null;
function viewFlows(process_id){
    var url = '_workflows.html?process=' + process_id;
    if (view_date !== null){
        url = url + '&amp;date=' + view_date.getFullYear() + '-' + (view_date.getMonth()+1) + '-' + view_date.getDate();
    }
    viewIt(url);
}

dojo.addOnLoad(function(){
    dojo.connect(dijit.byId('process_list'),'onDblClick', function(event){this.refresh();});
    dojo.connect(dijit.byId('actor_list'),'onDblClick', function(event){this.refresh();});
});