
Module("pythonkw","1.0.0", function(mod){

    var jsonrpc = imprt("jsonrpc");

    mod.PythonKw = Class(function(publ){
        publ.__init__ = function(kw){
            this.kw = kw;
            }

        publ.toJSON = function(){
            var pack = {};
            pack["pythonKwMaRkEr"] = this.kw;
            return jsonrpc.marshall(pack);
            }

        publ.kw;
    })

})
