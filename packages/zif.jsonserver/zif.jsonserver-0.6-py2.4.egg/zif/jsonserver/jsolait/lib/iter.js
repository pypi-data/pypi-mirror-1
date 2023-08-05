
Module("iter","$Revision: 80 $",function(mod){
mod.Iterator=Class(function(publ,supr){
publ.next=function(){
return undefined;
};
publ.__iter__=function(){
return this;
};
});
mod.Range=Class(mod.Iterator,function(publ,supr){
publ.__init__=function(start,end,step){
switch(arguments.length){
case 1:
this.start=0;
this.end=start;
this.step=1;
break;
case 2:
this.start=start;
this.end=end;
this.step=1;
break;
default:
this.start=start;
this.end=end;
this.step=step;
break;
}
this.current=this.start-this.step;
};
publ.next=function(){
if(this.current+this.step>this.end){
this.current=this.start;
return undefined;
}else{
this.current=this.current+this.step;
return this.current;
}
};
});
Range=mod.Range;
mod.ArrayItereator=Class(mod.Iterator,function(publ,supr){
publ.__init__=function(array){
this.array=array;
this.index=-1;
};
publ.next=function(){
this.index+=1;
if(this.index>=this.array.length){
return undefined;
}else{
return this.array[this.index];
}
};
});
mod.ObjectIterator=Class(mod.Iterator,function(publ,supr){
publ.__init__=function(obj){
this.obj=obj;
this.keys=[];
for(var n in obj){
this.keys.push(n);
}
this.index=-1;
};
publ.next=function(){
this.index+=1;
if(this.index>=this.keys.length){
return undefined;
}else{
var key=this.keys[this.index];
var rslt={key:key};
try{
rslt.value=this.obj[key];
}catch(e){
}
return rslt;
}
};
});
Array.prototype.__iter__=function(){
return new mod.ArrayItereator(this);
};
mod.IterationCallback=function(item,iteration){};
mod.Iteration=Class(function(publ,supr){
publ.__init__=function(iterable,thisObj,callback){
this.doStop=false;
this.thisObj=thisObj;
if(iterable.__iter__!==undefined){
this.iterator=iterable.__iter__();
}else{
this.iterator=new mod.ObjectIterator(iterable);
}
this.callback=callback;
};
publ.resume=function(){
this.doStop=false;
var item;
while(!this.doStop){
item=this.iterator.next();
if(item===undefined){
this.stop();
}else{
this.callback.call(this.thisObj==null?this:this.thisObj,item,this);
}
}
};
publ.stop=function(){
this.doStop=true;
};
publ.start=function(){
this.resume();
};
});
mod.AsyncIteration=Class(mod.Iteration,function(publ,supr){
publ.__init__=function(iterable,interval,thisObj,callback){
this.doStop=false;
this.thisObj=thisObj;
if(iterable.__iter__!==undefined){
this.iterator=iterable.__iter__();
}else{
this.iterator=new mod.ObjectIterator(iterable);
}
this.interval=interval;
this.callback=callback;
this.isRunning=false;
};
publ.stop=function(){
if(this.isRunning){
this.isRunning=false;
clearTimeout(this.timeout);delete iter.iterations[this.id];
}
};
publ.resume=function(){
if(this.isRunning==false){
this.isRunning=true;
var id=0;while(iter.iterations[id]!==undefined){
this.id++;
}
this.id=""+id;
iter.iterations[this.id]=this;
this.timeout=setTimeout("iter.handleAsyncStep('"+this.id+"')",this.interval);
}
};
publ.handleAsyncStep=function(){
if(this.isRunning){
tem=this.iterator.next();
if(item===undefined){
this.stop();
}else{
this.callback.call(this.thisObj==null?this:this.thisObj,item,this);
this.timeout=setTimeout("iter.handleAsyncStep('"+this.id+"')",this.interval);
}
}
};
});
iter=function(iterable,delay,thisObj,cb){
cb=arguments[arguments.length-1];
if((arguments.length==3)&&(typeof delay=='object')){
thisObj=delay;
delay=-1;
}else{
thisObj=null;
}
if(delay>-1){
var it=new mod.AsyncIteration(iterable,delay,thisObj,cb);}else{
var it=new mod.Iteration(iterable,thisObj,cb);
}
it.start();
return it;
};
iter.handleAsyncStep=function(id){
if(iter.iterations[id]){
iter.iterations[id].handleAsyncStep();
}
};
iter.iterations={};
mod.__main__=function(){
var testing=imprt('testing');
var task=function(){
var s='';
for(var i=0;i<10;i++){
s+=i;
}
};
r=[];
for(var i=0;i<100;i++){
r[i]=i;
}
print("for loop \t\t\t"+testing.timeExec(100,function(){
var s='';
for(var i=0;i<100;i++){
s+=r[i];
task();
}
}));
print("Range iter \t\t"+testing.timeExec(100,function(){
var s='';
iter(new mod.Range(100),function(item,i){
s+=r[item];
task();
});
}));
print("Array iter \t\t\t"+testing.timeExec(100,function(){
var s='';
iter(r,function(item,i){
s+=item;
task();
});
}));
print("for in on Array \t\t"+testing.timeExec(100,function(){
var s='';
for(var i in r){
s+=r[i];
task();
}
}));
r=[];
for(var i=0;i<100;i++){
r["k"+i]=i;
}
print("for in  on as.Array \t"+testing.timeExec(100,function(){
var s='';
for(var i in r){
s+=r[i];
task();
}
}));
r={};
for(var i=0;i<100;i++){
r["k"+i]=i;
}
print("for in on dictionary \t"+testing.timeExec(100,function(){
var s='';
for(var i in r){
s+=r[i];
task();
}
}));
r=[];
for(var i=0;i<100;i++){
r[i]=i;
}
print("for on Array + iter \t"+testing.timeExec(100,function(){
var s='';
for(i=r.__iter__();item=i.next()!==undefined;){
s+=item;
task();
}
}));
};
});
