function json_format(txt,compress/*是否为压缩模式*/){/* 格式化JSON源码(对象转换为JSON文本) */  
        var indentChar = '    ';   
        if(/^\s*$/.test(txt)){   
            // alert('数据为空,无法格式化! ');   
            return;   
        }   
        try{var data=eval('('+txt+')');}   
        catch(e){   
            //alert('数据源语法错误,格式化失败! 错误信息: '+e.description,'err');   
            return;   
        };   
        var draw=[],last=false,This=this,line=compress?'':'\n',nodeCount=0,maxDepth=0;   
           
        var notify=function(name,value,isLast,indent/*缩进*/,formObj){   
            nodeCount++;/*节点计数*/  
            for (var i=0,tab='';i<indent;i++ )tab+=indentChar;/* 缩进HTML */  
            tab=compress?'':tab;/*压缩模式忽略缩进*/  
            maxDepth=++indent;/*缩进递增并记录*/  
            if(value&&value.constructor==Array){/*处理数组*/  
                draw.push(tab+(formObj?('"'+name+'":'):'')+'['+line);/*缩进'[' 然后换行*/  
                for (var i=0;i<value.length;i++)   
                    notify(i,value[i],i==value.length-1,indent,false);   
                draw.push(tab+']'+(isLast?line:(','+line)));/*缩进']'换行,若非尾元素则添加逗号*/  
            }else   if(value&&typeof value=='object'){/*处理对象*/  
                    draw.push(tab+(formObj?('"'+name+'":'):'')+'{'+line);/*缩进'{' 然后换行*/  
                    var len=0,i=0;   
                    var all_keys = [];
                    for(var key in value) {
                        all_keys.push(key);
                        len++;   
                    };
                    function sort_by_id(id_type1, id_type2) {
                        var id1 = id_type1.split('_')[0]; 
                        var id2 = id_type2.split('_')[0];
                        try{var nid1=Number(id1);var nid2=Number(                        id2);}
                        catch(e){
                            return (id1<id2) ? -1 : 1; 
                        };
                        return (nid1<nid2) ? -1 : 1;
                    };
                    all_keys.sort(sort_by_id); 
                    for(var index in all_keys) {
                        key = all_keys[index];
                        notify(key,value[key],++i==len,indent,true);   
                    };
                    draw.push(tab+'}'+(isLast?line:(','+line)));/*缩进'}'换行,若非尾元素则添加逗号*/  
                }else{   
                        if(typeof value=='string')value='"'+value+'"';   
                        draw.push(tab+(formObj?('"'+name+'":'):'')+value+(isLast?'':',')+line);   
                };   
        };   
        var isLast=true,indent=0;   
        notify('',data,isLast,indent,false);   
        return draw.join('');   
    }  


function set_ace_editor() {
    var editor = ace.edit('ace-editor');
    editor.setTheme("ace/theme/github");
    var PyMode = require("ace/mode/json").Mode;
    editor.getSession().setMode(new PyMode());

    editor.getSession().setTabSize(4);
    editor.getSession().setUseSoftTabs(true);
    editor.getSession().setValue(json_format(editor.getSession().getValue(), false))
}

function send_ajax(url, method, send_msg, callback) {
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = callback;
    xmlhttp.open(method,url,true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send(send_msg);
    
}

function save_config(config_name) { 
    var editor = ace.edit('ace-editor');
    config_value = editor.getSession().getValue();
    
    try{var data= eval('('+config_value+')');}
    catch(e){
        alert('配置格式错误无法提交！）')
        return;
    }
    config_value = JSON.stringify(data);

    // ajax 发送保存配置数据
    function recall() {
        if (xmlhttp.readyState !=4) {
            document.getElementById("save_tag").innerHTML="正在保存..."
        }
        else if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            document.getElementById("save_tag").innerHTML="保存成功！"
            alert("保存成功！");
         }
        else {
            alert(xmlhttp.status);
            document.getElementById("save_tag").innerHTML="保存失败！"
        }
    }
    send_msg = "config_name="+config_name+"&config_value="+config_value;    
    send_ajax("/admin/save_config", "POST", send_msg, recall)
    

}

function modify_user(can_modify, type, key) {
    alert(can_modify);
    if (can_modify != 'True') {
        alert("只有管理员可以修改玩家数据！");
        return;
    }
    uid = document.getElementById("uid").value;
    value = document.getElementById(key).value;
    host = "/admin/modify_player";
    send_msg = "uid="+uid+"&type="+type+"&"+key+"="+value;
    url = host + send_msg;
    function recall() {
        if (xmlhttp.readyState == 4) {
            if (xmlhttp.status==200) {
                document.getElementById(type).innerHTML=xmlhttp
.responseText;
                alert("修改成功!");
            }
            else
                alert("修改玩家数据失败!");
        }
    }
    send_ajax(host, "POST", send_msg, recall);
}
