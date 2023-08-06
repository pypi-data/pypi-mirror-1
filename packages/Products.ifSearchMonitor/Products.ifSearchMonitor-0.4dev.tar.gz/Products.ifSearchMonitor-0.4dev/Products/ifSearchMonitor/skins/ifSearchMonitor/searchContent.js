
parent = window.opener;
window.onload = function(){parent.popSearch = window};
window.onunload = function(){parent.popSearch = false};

function closePopUp(){
    parent.popSearch = false;
    window.close();
}

function addRecommend(id, title){
    if(parent.hasItem(id))
        return;
    parent.addItem(id);
    var newField = parent.document.getElementById('readroot').cloneNode(true);
    newField.id = 'rc_selection';
    newField.style.display = 'block';
    var field = newField.childNodes;
    for(var i = 0; i < field.length; i++){
        if(field[i].type == 'hidden'){
            field[i].value = id;
        }
        if(field[i].id == 'rc_title'){
            field[i].innerHTML = title;
        }
    }
    var insertHere = parent.document.getElementById('writeroot');
    insertHere.parentNode.insertBefore(newField, insertHere);

    var none_sel = parent.document.getElementById('no_selection');
    if(none_sel)
        none_sel.style.display = 'none';
}

