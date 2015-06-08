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
                    for(var key in value)len++;   
                    for(var key in value)notify(key,value[key],++i==len,indent,true);   
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

function save_config(config_name) { 
    alert(config_name);
    var editor = ace.edit('ace-editor');
    config_value = editor.getSession().getValue();
    
    try{var data= eval('('+config_value+')');}
    catch(e){
        alert('配置格式错误无法提交！）')
        return;
    }

    // ajax 发送保存配置数据
    xmlhttp=new XMLHttpRequest();
    xmlhttp.onreadystatechange=function() {
        if (xmlhttp.readyState !=4) {
            document.getElementById("save_tag").innerHTML="正在保存..."
        }
        else if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            document.getElementById("save_tag").innerHTML="保存成功！"
         }
    }
    xmlhttp.open("POST","/admin/save_config",true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    send_msg = "config_name="+config_name+"&config_value="+config_value;    
    xmlhttp.send(send_msg);

}
