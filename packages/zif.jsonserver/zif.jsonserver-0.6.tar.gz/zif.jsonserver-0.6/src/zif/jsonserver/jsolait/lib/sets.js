
Module("sets","$Revision: 80 $",function(mod){
mod.ItemNotFoundInSet=Class(mod.Exception,function(publ,supr){
publ.set;
publ.item;
publ.__init__=function(set,item){
this.set=set;
this.item=item;
};
});
mod.Set=Class(function(publ,supr){
publ.__init__=function(elem){
this.items={};
var elems=[];
if(arguments.length>1){
elems=arguments;
}else if(arguments.length==1){
elems=arguments[0];
if(elems instanceof Array){
}else if(typeof elems=="string"){
elems=elems.split("");
}else if(elems.__iter__){
var i=iterable.__iter__();
var item;
while(item=i.next()!==undefined){
this.add(item);
}
return ;
}else{
throw new mod.Exception("Array,String or iterable object expected but found %s".format(elems));
}
}
for(var i=0;i<elems.length;i++){
this.add(elems[i]);
}
};
publ.add=function(item){
var h;
if(item.__hash__){
h='@'+item.__hash__();
}else{
h='#'+item;
}
this.items[h]=item;
return item;
};
publ.remove=function(item){
var h;
if(item.__hash__){
h='@'+item.__hash__();
}else{
h='#'+item;
}
if(this.items[h]===undefined){
throw new mod.ItemNotFoundInSet(this,item);
}else{
item=this.items[h];
delete this.items[h];return item;
}
};
publ.discard=function(item){
var h;
if(item.__hash__){
h='@'+item.__hash__();
}else{
h='#'+item;
}
item=this.items[h];
delete this.items[h];return item;
};
publ.contains=function(item){
var h;
if(item.__hash__){
h='@'+item.__hash__();
}else{
h='#'+item;
}
return(this.items[h]!==undefined);
};
publ.isSubSet=function(setObj){
for(var n in this.items){
if(setObj.contains(this.items[n])==false){
return false;
}
}
return true;
};
publ.isSuperSet=function(setObj){
return setObj.isSubSet(this);
};
publ.equals=function(setObj){
return(this.isSubSet(setObj)&&setObj.isSubSet(this));
};
publ.__equals__=function(setObj){
if(setObj instanceof publ.constructor){
return this.equals(setObj);
}else{
return false;
}
};
publ.union=function(setObj){
var ns=this.copy();
ns.unionUpdate(setObj);
return ns;
};
publ.intersection=function(setObj){
var ns=new mod.Set();
for(var n in this.items){
var item=this.items[n];
if(setObj.contains(item)){
ns.add(item);
}
}
return ns;
};
publ.difference=function(setObj){
var ns=new mod.Set();
for(var n in this.items){
var item=this.items[n];
if(setObj.contains(item)==false){
ns.add(item);
}
}
return ns;
};
publ.symmDifference=function(setObj){
var ns=this.difference(setObj);
return ns.unionUpdate(setObj.difference(this));
};
publ.unionUpdate=function(setObj){
for(var n in setObj.items){
this.add(setObj.items[n]);
}
return this;
};
publ.intersectionUpdate=function(setObj){
for(var n in this.items){
var item=this.items[n];
if(setObj.contains(item)==false){
this.remove(item);
}
}
return this;
};
publ.differenceUpdate=function(setObj){
for(var n in this.items){
var item=this.items[n];
if(setObj.contains(item)){
this.remove(item);
}
}
return this;
};
publ.symmDifferenceUpdate=function(setObj){
var union=setObj.difference(this);
this.differenceUpdate(setObj);
return this.unionUpdate(union);
};
publ.copy=function(){
var ns=new mod.Set();
return ns.unionUpdate(this);
};
publ.clear=function(){
this.items={};
};
publ.toArray=function(){
var a=[];
for(var n in this.items){
a.push(this.items[n]);
}
return a;
};
publ.toString=function(){
var items=[];
for(var n in this.items){
items.push(this.items[n]);
}
return "{"+items.join(",")+"}";
};
});
mod.__main__=function(){
var s1=new mod.Set("0123456");
var s2=new mod.Set("3456789");
var testing=imprt('testing');
print(testing.test(function(){
testing.assertEquals("checking %s | %s".format(s1,s2),new mod.Set("0123456789"),s1.union(s2));
testing.assertEquals("checking %s | %s".format(s2,s1),
new mod.Set("0123456789"),s2.union(s1));
testing.assertEquals("checking %s & %s".format(s1,s2),
new mod.Set("3456"),s1.intersection(s2));
testing.assertEquals("checking %s & %s".format(s2,s1),
new mod.Set("3456"),s2.intersection(s1));
testing.assertEquals("checking %s - %s".format(s1,s2),
new mod.Set("012"),s1.difference(s2));
testing.assertEquals("checking %s - %s".format(s2,s1),
new mod.Set("789"),s2.difference(s1));
testing.assertEquals("checking %s ^ %s".format(s1,s2),
new mod.Set("012789"),s1.symmDifference(s2));
testing.assertEquals("checking %s ^ %s".format(s2,s1),
new mod.Set("012789"),s2.symmDifference(s1));
}));
};
});
