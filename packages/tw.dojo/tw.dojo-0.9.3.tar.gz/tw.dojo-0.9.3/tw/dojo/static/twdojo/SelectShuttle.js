dojo.provide("twdojo.SelectShuttle")
dojo.require("dijit._Widget")
dojo.require("dijit.form.Button")
dojo.require("dijit.form.MultiSelect")
dojo.require("dojo.string")

dojo.declare("twdojo.SelectShuttle",
    [dijit._Widget],
    {
        constructor: function(){
            this.el= arguments[1];
            var selects = dojo.query("select", this.el);

            this.src = new dijit.form.MultiSelect({ name: selects[0].id, parent:this }, selects[0]);
            this.src.containerNode.attachedDigit = this

            this.dst = new dijit.form.MultiSelect({ name: selects[1].id, parent:this }, selects[1]);
            this.dst.containerNode.attachedDigit = this

            var buttons = dojo.query("button", this.el);
            this.allRightButton = new dijit.form.Button({name:   buttons[0].id, 
                                                         parent: this, 
                                                         onClick:   function(){this.parent.moveAllRight()}}, 
                                                        buttons[0]);
            this.rightButton    = new dijit.form.Button({name:buttons[1].id,
                                                         parent: this, 
                                                         onClick:   function(){this.parent.moveRight()}}, 
                                                         buttons[1]);
            this.leftButton     = new dijit.form.Button({name:buttons[2].id,
                                                         parent: this, 
                                                         onClick:   function(){this.parent.moveLeft()}},
                                                         buttons[2]);
            this.allLeftButton  = new dijit.form.Button({name:   buttons[3].id,
                                                         parent: this, 
                                                         onClick:   function(){this.parent.moveAllLeft()}},
                                                        buttons[3]);
            this.form = this.dst.containerNode.form;
            
            //register the shuttles for this form
            if (this.form.shuttles === undefined){
                this.form.shuttles = []
                }
            this.form.shuttles[this.form.shuttles.length]=this
            
            //set up double click
            dojo.connect(this.src.containerNode, "ondblclick", function(e){
                        this.attachedDigit.moveRight()
            });
            dojo.connect(this.dst.containerNode, "ondblclick", function(e){
                        this.attachedDigit.moveLeft()
            });
            
            // ensure that when the "submit" button is clicked, all of the items in the "dst" 
            // select are selected
            dojo.connect(this.form, "onclick", function(e){
                if (e.target.type == 'submit'){
                    for (i=0; i<this.shuttles.length; i++){
                        options = this.shuttles[i].dst.containerNode.options;
                        for(j=0; j<options.length; j++){
                            option = options[j];
                            option.selected = "selected";
                        }
                    }
                }
            });
        },
        moveLeft: function(e){
            this.move(this.dst, this.src);
        },
        moveRight: function(e){
            this.move(this.src, this.dst);
        },
        moveAllLeft: function(e){
            this.move(this.dst, this.src, true);
        },
        moveAllRight: function(e){
            this.move(this.src, this.dst, true);
        },
        move: function(src, dst, all){
            if (all){
                // move all items
                options = src.containerNode.options;
                for(j=0; j<options.length; j++){
                    option = options[j];
                    option.selected = "selected";
                }
            }
            dst.addSelected(src);
        },
    }
);