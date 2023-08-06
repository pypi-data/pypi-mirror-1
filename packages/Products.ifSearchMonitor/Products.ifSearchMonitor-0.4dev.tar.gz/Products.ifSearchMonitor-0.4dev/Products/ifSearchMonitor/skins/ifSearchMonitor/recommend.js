var popSearch = false;

function popUpSearch(){
    popSearch = window.open('browseContent', 'searchContent', 'location=0,status=0,toolbar=0,menubar=0,resizable=0,scrollbars=1,width=350,height=450');
}

function delRecommended(section){
    var id = false;
    var field = section.parentNode.childNodes;
    for(var i = 0; i < field.length; i++){
        if(field[i].type == 'hidden'){
            id = field[i].value;
        }
    }
    removeItem(id);
    section.parentNode.parentNode.removeChild(section.parentNode);
}

function delSavedRecommended(section, id){
    delRecommended(section);
    removeRecommend(id);
}


function removeRecommend(id){
    var newField = document.getElementById('removereadroot').cloneNode(true);
    newField.id = 'rc_remove';
    newField.style.display = 'block';
    var field = newField.childNodes;
    for(var i = 0; i < field.length; i++){
        if(field[i].type == 'hidden'){
            field[i].value = id;
        }
    }
    var insertHere = document.getElementById('removewriteroot');
    insertHere.parentNode.insertBefore(newField, insertHere);
    return false;
}

/* ------------- */
selected = new Array();

function addItem(item){
    var i = selected.length;
    selected[i] = item;
}

function hasItem(item){
    var i;
    for(i = 0; i < selected.length; i++){
        if (selected[i] == item) {
            return true;
        }
    }
    return false;
}

function removeItem(item){
    var i = 0;
    while (i < selected.length){
        if (selected[i] == item) {
            selected.splice(i, 1);
        }else{
            i++;
        }
    }
}
