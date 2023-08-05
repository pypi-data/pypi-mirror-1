
Class=function(name,bases,classScope){
var args=[];
for(var i=0;i<arguments.length;i++){
args[i]=arguments[i];
}
classScope=args.pop();
if((args.length>0)&&(typeof args[0]=='string')){
name=args.shift();
}else{
name="anonymous";
}
var bases=args;
var __class__={__isArray__:false,
__name__:name,
__bases__:bases,
__id__:Class.__idcount__++,
__hash__:function(){
return this.__id__;
},
__str__:function(){
return "[class %s]".format(this.__name__);
}
};
var baseProtos=[];var proto;if(bases.length==0){proto={};
proto.__str__=function(){
return "[%s %s]".format(this.__class__.prototype.__call__===undefined?'object':'callable',this.__class__.__name__);
};
proto.toString=proto.__str__;
__class__.__bases__=[Object];
}else{var baseProto;
for(var i=0;i<bases.length;i++){
var baseClass=bases[i];
baseProtos.push(baseClass.prototype);
if(baseClass.__createProto__!==undefined){
baseProto=baseClass.__createProto__(bases);
}else{
baseProto=new baseClass(Class);
}
__class__.__isArray__=__class__.__isArray__||baseClass.__isArray__;
if(i==0){proto=baseProto;
}else{for(var key in baseProto){
if(proto[key]===undefined){
proto[key]=baseProto[key];
}
}
}
for(var key in baseClass){
if((key!='prototype')&&(__class__[key]===undefined)){
__class__[key]=baseClass[key];
}
}
}
proto.toString=proto.__str__;
}
if(proto.__hash__===undefined){
proto.__hash__=function(){
if(this.__id__===undefined){
this.__id__=Class.__idcount__++;
}
return this.__id__;
};
}
proto.__class__=__class__;
var privId='__priv__'+__class__.__id__;
if(classScope.length-1>baseProtos.length){
classScope.apply(this,[proto,privId].concat(baseProtos));
}else{
classScope.apply(this,[proto].concat(baseProtos));
}
if(proto.__call__){
var NewClass=function(calledBy){
if(calledBy!==Class){
var rslt=function(){
return rslt.__call__.apply(rslt,arguments);
};
var privId='__priv__'+arguments.callee.__id__;
rslt[privId]={};
var proto=arguments.callee.prototype;
for(var n in proto){
rslt[n]=proto[n];
}
rslt.constructor=arguments.callee;
rslt.toString=proto.__str__;
if(rslt.__init__){
rslt.__init__.apply(rslt,arguments);
}
return rslt;
}
};
}else if(__class__.__isArray__){
var NewClass=function(calledBy){
if(calledBy!==Class){
rslt=[];
var privId='__priv__'+arguments.callee.__id__;
rslt[privId]={};
var proto=arguments.callee.prototype;
for(var n in proto){
rslt[n]=proto[n];
}
rslt.constructor=proto;
rslt.toString=proto.__str__;
if(rslt.__init__){
rslt.__init__.apply(rslt,arguments);
}else{if(arguments.lengt==1){
rslt.length=arguments[0];
}else{
for(var i=0;i<arguments.length;i++){
rslt.push(arguments[i]);
}
}
}
return rslt;
}
};
}else{
var NewClass=function(calledBy){
if(calledBy!==Class){
var privId='__priv__'+arguments.callee.__id__;
this[privId]={};
if(this.__init__){
this.__init__.apply(this,arguments);
}}
};
}
proto.constructor=NewClass;
proto.__class__=NewClass;NewClass.prototype=proto;
for(var key in __class__){
NewClass[key]=__class__[key];
}
NewClass.toString=__class__.__str__;
return NewClass;
};Class.__idcount__=0;
Class.toString=function(){
return "[object Class]";
};
Class.__createProto__=function(){throw "Can't use Class as a base class.";
};
Array.__isArray__=true;
Array.__str__=Array.toString=function(){return "[class Array]";};
Array.__createProto__=function(){var r=[];r.__str__=Array.prototype.toString;return r;};
Object.__str__=Object.toString=function(){return "[class Object]";};
Function.__createProto__=function(){throw "Cannot inherit from Function. implement the callabel interface instead using YourClass::__call__.";};
Module=function(name,version,moduleScope){
var newMod={};
newMod.name=name;
newMod.version=version;
newMod.__sourceURI__=Module.currentURI;
newMod.toString=function(){
return "[module '%s' version: %s]".format(this.name,this.version);
};
newMod.Exception=Class(Module.Exception,function(publ,supr){
publ.module=newMod;
});
try{moduleScope.call(newMod,newMod);
}catch(e){
throw new Module.ModuleScopeExecFailed(newMod,e);
}
for(var n in newMod){
var obj=newMod[n];
if(typeof obj=='function'){
obj.__name__=n;
}
}
jsolait.registerModule(newMod);
return newMod;
};
Module.toString=function(){
return "[object Module]";
};
Module.__createProto__=function(){throw "Can't use Module as a base class.";
};
Module.Exception=Class("Exception",function(publ){
publ.__init__=function(msg,trace){
this.name=this.constructor.__name__;
this.message=''+msg;
this.trace=trace;
};
publ.__str__=function(){
var s="%s %s".format(this.name,this.module);
return s;
};
publ.toTraceString=function(indent){
indent=indent==null?0:indent;
var s="%s in %s:\n%s".format(this.name,this.module,this.message.indent(4)).indent(indent);
if(this.trace){
if(this.trace.toTraceString){
s+=('\n\nbecause:\n'+this.trace.toTraceString(indent+4));
}else{
s+=(this.trace+'\n').indent(indent+4);
}
}
return s;
};
publ.name;publ.message;
publ.module="jsolait";
publ.trace;});
Module.ModuleScopeExecFailed=Class("ModuleScopeExecFailed",Module.Exception,function(publ,supr){
publ.__init__=function(module,trace){
supr.__init__.call(this,"Failed to run the module scope for %s".format(module),trace);
this.failedModule=module;
};
publ.module;
});
Module("jsolait","$Revision: 80 $",function(mod){
jsolait=mod;
mod.modules={};
mod.knownModuleURIs={codecs:"%(baseURI)slib/codecs.js",
pythonkw:"%(baseURI)slib/pythonkw.js",
crypto:"%(baseURI)slib/crypto.js",
dom:"%(baseURI)slib/dom.js",
forms:"%(baseURI)slib/forms.js",
iter:"%(baseURI)slib/iter.js",
jsonrpc:"%(baseURI)slib/jsonrpc.js",
lang:"%(baseURI)slib/lang.js",
sets:"%(baseURI)slib/sets.js",
testing:"%(baseURI)slib/testing.js",
urllib:"%(baseURI)slib/urllib.js",
xml:"%(baseURI)slib/xml.js",
xmlrpc:"%(baseURI)slib/xmlrpc.js"};
mod.moduleSearchURIs=[".","%(baseURI)slib"];
mod.baseURI = "/++resource++jsolait";
var getHTTP=function(){
var obj;
try{obj=new XMLHttpRequest();
}catch(e){
try{obj=new ActiveXObject("Msxml2.XMLHTTP.4.0");
}catch(e){
try{obj=new ActiveXObject("Msxml2.XMLHTTP");
}catch(e){
try{obj=new ActiveXObject("microsoft.XMLHTTP");}catch(e){
throw new mod.Exception("Unable to get an HTTP request object.");
}
}}
}
return obj;
};
mod.loadURI=function(uri,headers){
headers=(headers!==undefined)?headers:[];
try{
var xmlhttp=getHTTP();
xmlhttp.open("GET",uri,false);
for(var i=0;i<headers.length;i++){
xmlhttp.setRequestHeader(headers[i][0],headers[i][1]);}
xmlhttp.send("");
}catch(e){
throw new mod.LoadURIFailed(uri,e);
}
if(xmlhttp.status==200||xmlhttp.status==0||xmlhttp.status==null){
var s=new String(xmlhttp.responseText);
s.__sourceURI__=uri;
return s;
}else{
throw new mod.LoadURIFailed(uri,new mod.Exception("Server did not respond with 200"));
}
};
mod.LoadURIFailed=Class(mod.Exception,function(publ,supr){
publ.__init__=function(sourceURI,trace){
supr.__init__.call(this,"Failed to load file: '%s'".format(sourceURI.indent(2)),trace);
this.sourceURI=sourceURI;
};
publ.sourceURI;
});
mod.__imprt__=function(name){
if(mod.modules[name]){return mod.modules[name];
}else{
var src,modPath;
if(mod.knownModuleURIs[name]!=undefined){
modPath=mod.knownModuleURIs[name].format(mod);
try{src=mod.loadURI(modPath);
}catch(e){
throw new mod.ImportFailed(name,[modPath],e);
}
}
if(src==null){var failedURIs=[];
for(var i=0;i<mod.moduleSearchURIs.length;i++){
modPath="%s/%s.js".format(mod.moduleSearchURIs[i].format(mod),name.split(".").join("/"));
try{
src=mod.loadURI(modPath);
break;
}catch(e){
failedURIs.push(e.sourceURI);
}
}
if(src==null){
throw new mod.ImportFailed(name,failedURIs);
}
}
try{var srcURI=src.__sourceURI__;
src='Module.currentURI="%s";\n%s\nModule.currentURI=null;\n'.format(src.__sourceURI__.replace(/\\/g,'\\\\'),src);
var f=new Function("",src);f();
}catch(e){
throw new mod.ImportFailed(name,[srcURI],e);
}
return mod.modules[name];}
};
mod.ImportFailed=Class(mod.Exception,function(publ,supr){
publ.__init__=function(moduleName,moduleURIs,trace){
supr.__init__.call(this,"Failed to import module: '%s' from:\n%s".format(moduleName,moduleURIs.join(',\n').indent(2)),trace);
this.moduleName=moduleName;
this.moduleURIs=moduleURIs;
};
publ.moduleName;
publ.moduleURIs;
});
imprt=function(name){
return mod.__imprt__(name);
};
mod.__registerModule__=function(modObj,modName){
if(modName!='jsolait'){
return mod.modules[modName]=modObj;
}
};
mod.registerModule=function(modObj,modName){
modName=modName===undefined?modObj.name:modName;
return mod.__registerModule__(modObj,modName);
};
var FormatSpecifier=function(s){
var s=s.match(/%(\(\w+\)){0,1}([ 0-]){0,1}(\+){0,1}(\d+){0,1}(\.\d+){0,1}(.)/);
if(s[1]){
this.key=s[1].slice(1,-1);
}else{
this.key=null;
}
this.paddingFlag=s[2];
if(this.paddingFlag==""){
this.paddingFlag=" ";}
this.signed=(s[3]=="+");
this.minLength=parseInt(s[4]);
if(isNaN(this.minLength)){
this.minLength=0;
}
if(s[5]){
this.percision=parseInt(s[5].slice(1,s[5].length));
}else{
this.percision=-1;
}
this.type=s[6];
};
String.prototype.format=function(){
var sf=this.match(/(%(\(\w+\)){0,1}[ 0-]{0,1}(\+){0,1}(\d+){0,1}(\.\d+){0,1}[dibouxXeEfFgGcrs%])|([^%]+)/g);
if(sf){
if(sf.join("")!=this){
throw new mod.Exception("Unsupported formating string.");
}
}else{
throw new mod.Exception("Unsupported formating string.");
}
var rslt="";
var s;
var obj;
var cnt=0;
var frmt;
var sign="";
for(var i=0;i<sf.length;i++){
s=sf[i];
if(s=="%%"){
s="%";
}else if(s=="%s"){if(cnt>=arguments.length){
throw new mod.Exception("Not enough arguments for format string.");
}else{
obj=arguments[cnt];
cnt++;
}
if(obj===null){
obj="null";
}else if(obj===undefined){
obj="undefined";
}
s=obj.toString();
}else if(s.slice(0,1)=="%"){
frmt=new FormatSpecifier(s);if(frmt.key){if((typeof arguments[0])=="object"&&arguments.length==1){
obj=arguments[0][frmt.key];
}else{
throw new mod.Exception("Object or associative array expected as formating value.");
}
}else{if(cnt>=arguments.length){
throw new mod.Exception("Not enough arguments for format string.");
}else{
obj=arguments[cnt];
cnt++;
}
}
if(frmt.type=="s"){if(obj===null){
obj="null";
}else if(obj===undefined){
obj="undefined";
}
s=obj.toString().pad(frmt.paddingFlag,frmt.minLength);
}else if(frmt.type=="c"){if(frmt.paddingFlag=="0"){
frmt.paddingFlag=" ";}
if(typeof obj=="number"){s=String.fromCharCode(obj).pad(frmt.paddingFlag,frmt.minLength);
}else if(typeof obj=="string"){
if(obj.length==1){s=obj.pad(frmt.paddingFlag,frmt.minLength);
}else{
throw new mod.Exception("Character of length 1 required.");
}
}else{
throw new mod.Exception("Character or Byte required.");
}
}else if(typeof obj=="number"){
if(obj<0){
obj=-obj;
sign="-";}else if(frmt.signed){
sign="+";}else{
sign="";
}
switch(frmt.type){
case "f":case "F":
if(frmt.percision>-1){
s=obj.toFixed(frmt.percision).toString();
}else{
s=obj.toString();
}
break;
case "E":case "e":
if(frmt.percision>-1){
s=obj.toExponential(frmt.percision);
}else{
s=obj.toExponential();
}
s=s.replace("e",frmt.type);
break;
case "b":s=obj.toString(2);
s=s.pad("0",frmt.percision);
break;
case "o":s=obj.toString(8);
s=s.pad("0",frmt.percision);
break;
case "x":s=obj.toString(16).toLowerCase();
s=s.pad("0",frmt.percision);
break;
case "X":s=obj.toString(16).toUpperCase();
s=s.pad("0",frmt.percision);
break;
default:s=parseInt(obj).toString();
s=s.pad("0",frmt.percision);
break;
}
if(frmt.paddingFlag=="0"){s=s.pad("0",frmt.minLength-sign.length);
}
s=sign+s;s=s.pad(frmt.paddingFlag,frmt.minLength);}else{
throw new mod.Exception("Number required.");
}
}
rslt+=s;
}
return rslt;
};
String.prototype.pad=function(flag,len){
var s="";
if(flag=="-"){
var c=" ";
}else{
var c=flag;
}
for(var i=0;i<len-this.length;i++){
s+=c;
}
if(flag=="-"){
s=this+s;
}else{
s+=this;
}
return s;
};
String.prototype.indent=function(indent){
var out=[];
var s=this.split('\n');
for(var i=0;i<s.length;i++){
out.push(' '.mul(indent)+s[i]);
}
return out.join('\n');
};
String.prototype.mul=function(l){
var a=new Array(l+1);
return a.join(this);
};
mod.test=function(){
};
});
importModule=imprt
