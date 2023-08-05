
Module("testing","$Revision: 80 $",function(mod){
mod.minProfileTime=500;
mod.timeExec=function(repeat,fn){
var args=[];
for(var i=2;i<arguments.length;i++){
args.push(arguments[i]);
}
var t=(new Date()).getTime();
for(var i=0;i<=repeat;i++){
fn.apply(null,args);}
return((new Date()).getTime()-t)/(repeat+1);
};
mod.profile=function(min,fn){
if(arguments.length==1){
fn=min;
min=mod.minProfileTime;
}
var args=[];
for(var i=2;i<arguments.length;i++){
args.push(arguments[i]);
}
var cnt=0;
var t1=(new Date()).getTime();
t2=t1;
while(t2-t1<min){
cnt++;
fn.apply(null,args);t2=(new Date()).getTime();
}
return(t2-t1)/cnt;
};
mod.Test=Class(function(publ,supr){
publ.__init__=function(testScope){
this.testScope=testScope;
};
publ.run=function(){
this.failed=false;
this.error=null;
this.startTime=(new Date()).getTime();
try{
this.testScope();
}catch(e){
if(e instanceof mod.AssertFailed){
this.error=e;
this.failed=true;
}else{
throw new mod.Exception("Failed to run test.",e);
}
}
this.endTime=(new Date()).getTime();
this.duration=this.endTime-this.startTime;
};
publ.report=function(){
if(this.error){
return "Test has failed after %s ms due to:\n\n%s".format(this.duration,this.error.toTraceString().indent(4));
}else{
return "Test completed in %s ms".format(this.duration);
}
};
publ.failed=false;
publ.error;
publ.startTime;
publ.endTime;
publ.duration;
});
mod.test=function(testScope){
var t=new mod.Test(testScope);
t.run();
return t.report();
};
mod.AssertFailed=Class(mod.Exception,function(publ,supr){
publ.__init__=function(comment,failMsg){
this.failMessage=failMsg;
this.comment=comment;
supr.__init__.call(this,"%s failed: %s".format(comment,failMsg));
};
});
mod.assert=function(comment,value,failMsg){
if(typeof comment=='boolean'){
failMsg=value;
value=comment;
comment='';
}
if(value!==true){
throw new mod.AssertFailed(comment,failMsg===undefined?"Expected true but found: %s".format(value):failMsg);
}};
mod.assertTrue=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,value===true,"Expected true but found: %s".format(value));};
mod.assertFalse=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,value===false,"Expected false but found: %s".format(value));};
mod.assertEquals=function(comment,value1,value2){
if(arguments.length==2){
value2=value1;
value1=comment;
comment='';
}
if((value1!=null)&&(value1.__equals__)||((value2!=null)&&(value2.__equals__))){
mod.assert(comment,value1.__equals__(value2),"Expected (using __equals__) %s === %s.".format(value1,value2));}else{
mod.assert(comment,value1===value2,"Expected %s === %s.".format(value1,value2));}};
mod.assertNotEquals=function(comment,value1,value2){
if(arguments.length==2){
value2=value1;
value1=comment;
comment='';
}
if((value1!=null)&&(value1.__equals__)||((value2!=null)&&(value2.__equals__))){
mod.assert(comment,!value1.__equals__(value2),"Expected (using __equals__) %s !== %s.".format(value1,value2));}else{
mod.assert(comment,value1!==value2,"Expected %s !== %s.".format(value1,value2));}};
mod.assertNull=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,value===null,"Expected %s === null.".format(value));};
mod.assertNotNull=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,value!==null,"Expected %s !== null.".format(value));};
mod.assertUndefined=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,value===undefined,"Expected %s === undefined.".format(value));
};
mod.assertNotUndefined=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,value!==undefined,"Expected %s !== undefined".format(value));};
mod.assertNaN=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,isNaN(value)===true,"Expected %s === NaN.".format(value));};
mod.assertNotNaN=function(comment,value){
if(arguments.length==1){
value=comment;
comment='';
}
mod.assert(comment,isNaN(value)!==true,"Expected %s !== NaN".format(value));
};
mod.fail=function(comment){
throw new mod.AssertFailed(comment,"Fail was called");
};
mod.objectKeys=function(obj){
var keys=[];
for(var n in obj){
keys.push(n);
}
return keys;
};
mod.__main__=function(){
print(mod.test(function(){
mod.assert(true);
mod.assertTrue(true);
mod.assertFalse(false);
mod.assertNull(null);
mod.assertNotNull(undefined);
mod.assertNotNull('');
mod.assertNotNull({});
mod.assertNotNull(0);
mod.assertUndefined(undefined);
mod.assertNotUndefined(null);
mod.assertNaN(NaN);
mod.assertNotNaN(435);
mod.assertEquals(1,1);
mod.assertEquals("a","a");
mod.assertEquals(null,null);
mod.assertEquals(undefined,undefined);
mod.assertEquals(mod,mod);
mod.assertNotEquals(1,2);
mod.assertNotEquals(null,undefined);
mod.assertNotEquals(mod,{});
}));
};
});
