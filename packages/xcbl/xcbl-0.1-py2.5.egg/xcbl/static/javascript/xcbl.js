function checkChanged (event)
{
    if (!event.src().checked) {
        removeElement(event.src().parentNode)
    }
}

function otherEntered (event)
{
    txtEntryChanged = event.src();
    val = txtEntryChanged.value;
    if (!/\S/.test(val)) {  // do not accept all-whitespace
        return;
    }
    
    checkBoxListName = getNodeAttribute(txtEntryChanged, "checkBoxListName");
    newCheckBoxId = checkBoxListName + "_" + val;
    newBox = INPUT({'type':'checkbox',
                                    'name': checkBoxListName,
                                    'id': newCheckBoxId,
                                    'value': val,
                                    'checked': true});
    labl = LABEL({'for':newCheckBoxId, 'class':'fieldlabel'}, SPAN({'class':'handentry'}, ' ' + val));
    newNode = LI(null, newBox, labl);

    listItemNode = getNodeAttribute(txtEntryChanged, "insert_before");
    // must install MochiKit 1.4 to get insertSiblingNodesBefore
    try {
        insertSiblingNodesBefore(listItemNode, newNode);
    }
    catch (e) {
        appendChildNodes($(listItemNode).parentNode, newNode);
    }
    MochiKit.Signal.connect(newBox, 'onchange', checkChanged);
    event.src().value = '';
}
