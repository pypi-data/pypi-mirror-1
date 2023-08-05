
Module("dom","$Revision: 80 $",function(mod){
var sets=imprt("sets");
mod.Event=Class(function(publ,supr){
publ.type=null;
});
mod.EventTarget=Class(function(publ,supr){
publ.__init__=function(){
this.eventListeners={};
};
publ.dispatchEvent=function(evt){
if(this.eventListeners[evt.type]){
var l=this.eventListeners[evt.type].items;
for(var h in l){
l[h].handleEvent(evt);
}
}
};
publ.addEventListener=function(evtType,listener,useCapture){
if(this.eventListeners[evtType]===undefined){
this.eventListeners[evtType]=new sets.Set();
}
this.eventListeners[evtType].add(listener);
};
publ.removeEventListener=function(evtType,listener,useCapture){
if(this.eventListeners[evtType]){
this.eventListeners[evtType].discard(listener);
}
};
});
mod.EventListener=Class(function(publ){
publ.handleEvent=function(evt){
if(this[evt.type]){
this[evt.type](evt);
}
};
});
mod.EventListenerTarget=Class(mod.EventTarget,mod.EventListener,function(publ,supr){
});
});
