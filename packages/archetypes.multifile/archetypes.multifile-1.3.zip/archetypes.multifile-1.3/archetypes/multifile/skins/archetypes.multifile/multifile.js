
//newdiv.innerHTML = "<input type=\"file\" size=\"30\" tabindex=\"\">" + num+"<a href=\"javascript:;\" onclick=\"removeEvent(\'"+divIdName+"\')\">remove</a><br>";


function addEvent(fieldname)
{
    var ni = document.getElementById('myDiv');
    var numi = document.getElementById('theValue');
    var num = (document.getElementById("theValue").value -1)+ 2;
    var rm_label = document.getElementById('multifile-remove-label').value;
    
    // Check if the last one is empty
    if (num > 1) {
        var last = ni.lastElementChild;
        if (last != null && last.firstElementChild.value == "") 
            return false;
    }
    numi.value = num;
    
    var divIdName = "my"+num+"Div";
    var newdiv = document.createElement('div');
    newdiv.setAttribute("id",divIdName);
    newdiv.innerHTML = "<input type=\"file\" onchange=\"return addEvent('"+fieldname+"')\" size=\"30\" tabindex=\"\"     name=\""+fieldname+":list\" id=\""+fieldname+":list\">&nbsp;<a href=\"javascript:;\" onclick=\"return removeEvent(\'"+divIdName+"\',\'"+fieldname+"\')\">"+rm_label+"</a><br>";
    ni.appendChild(newdiv);
    return false;
}

function removeEvent(divNum, fieldname)
{
    var d = document.getElementById('myDiv');
    var olddiv = document.getElementById(divNum);
    
    var last = d.lastElementChild;
    if (last != null && last.id == divNum)
        return false;
    
    d.removeChild(olddiv);
    return false;
}

function deleteFile(ele){
    if (ele){
        chkbox = document.getElementById(ele);
        chkbox.checked = true;
        chkbox.parentNode.style.display = 'none';
    }
    return false;
}
