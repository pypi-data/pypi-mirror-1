var ui_dragging = false;

function setHeightOfEmptyDropZone(){
    //set height of empty dropzones
    jq('.simplelayout-content [id*=slot]').each(function(i,v){
        var v_obj = jq(v);
        if (v_obj.height()==0){
            v_obj.css('height','300px');    
        }else{
         v_obj.css('height','auto');
                }
        });
}

function refreshSimplelayoutDragndropOrdering() { 
    
    var sl_content = jq('.simplelayout-content');
    
    jq('.BlockOverallWrapper .sl-controls').bind("mousedown",function(e){
        jq(this).toggleClass('mouseToggler');
        })

    jq('.BlockOverallWrapper .sl-controls').bind("mouseup",function(e){
        jq(this).toggleClass('mouseToggler');
        })

    jq('.simplelayout-content [id*=slot]').sortable({
		items: '.BlockOverallWrapper',
        handle: jq('.BlockOverallWrapper .sl-controls'),
        scroll : true,
		forcePlaceholderSize : false,
		placeholder: 'placeholder',
        connectWith: jq('.simplelayout-content [id*=slot]'),
        /* appendTo : '.BlockOverallWrapper',*/
		opacity: 0.5,
		tolerance:'pointer',
		start: function(e,ui) {
		    ui_dragging = true;
		    ui.placeholder.css("width", ui.item.width()-1);
		    ui.placeholder.css("height", ui.item.height()-1);

		},
		update: function(e, ui){
            var ids = new Array();
            jq('.BlockOverallWrapper').each(function(i, o) { ids.push(o.id); });
            ids = ids.join(',');
            var slot = jq(e.target).attr('id');
            var column = jq(e.target).attr('class');
            
            var obj_uid = jq(ui.item[0]).attr('id');
            var activeLayout = jq('.sl-layout.active',ui.item);

                    
            //jq.post('sl_dnd_saveorder', { uids : ids ,slot:slot,column:column,obj_uid:obj_uid});
            //refresh paragraph after reordering
            ajaxManager.add({url:'sl_dnd_saveorder',
                            data:{ uids : ids ,slot:slot,column:column,obj_uid:obj_uid},
                            success:function(){
                                if (activeLayout.length != 0){
                                    simplelayout.refreshParagraph(activeLayout[0]);
                                    }
                                }
                            });
            
            
            
            
		},
        /*change: function(e, ui){
            setHeightOfEmptyDropZone();

		}, */
		stop: function(e, ui){
		    ui.item.removeAttr("style");
            setHeightOfEmptyDropZone();
            
            jq(".simplelayout-content").trigger('afterReorder');
            
		}

    })
    
    if(simplelayout.edit_mode=="1"){
        sl_content.sortable('enable');
    }else{
        sl_content.sortable('disable');
    }
    
    sl_content.bind("toggleeditmode", function(e){
        sl_content.sortable('enable');
    });

    setHeightOfEmptyDropZone();
    
}

jq(refreshSimplelayoutDragndropOrdering);

