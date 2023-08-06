/*
######################################################################### 
# Copyright (C) 2007, 2008, 2009 
# Alex Clemesha <alex@clemesha.org> & Dorian Raymer <deldotdr@gmail.com>
# 
# This module is part of codenode, and is distributed under the terms 
# of the BSD License:  http://www.opensource.org/licenses/bsd-license.php
#########################################################################

 Notebook.Async - The AJAX functions -- this is where all async 
            communications are defined.

 */
BASE_URL = '/asyncnotebook/'+document.location.pathname.split('/')[2]+'/';
Notebook.Async = function() {
};


// Should Async be a class or not?

Notebook.Async.initialize = function() {
    // eval json written to html body by server
    var url = BASE_URL+'nbobject';
    var success = function (res) {
        Notebook.Load.takeCellsData(res);
        }
    $.getJSON(url, success);
    Notebook.Async.startEngine();
    Notebook.Indicator.endMsg();
};

Notebook.Async.startEngine = function() {
    var path = BASE_URL+'start';
    $.ajax({
        url:path,
        type:'GET',
        dataType:'json',
        success: function(result) {
            //engine started
            //console.info(result)
        },
        error: function(result) {
            //engine failed to start
            //console.info(result)
        }});
};

Notebook.Async.signalKernel = function(action) {
    var self = Notebook.Async;
    var path = BASE_URL+'kernel';
    var data = {'action':action};
    $.ajax({
            url:path,
            type:'POST',
            data:data,
            dataType:'json',
            success:self.signalSuccess,
            error:self.signalError});
};

Notebook.Async.signalSuccess = function(result) {
};

Notebook.Async.signalError = function(result) {
};

Notebook.Async.evalCell = function(cellid, input) {
    var self = Notebook.Async;
    var path = BASE_URL+'eval';
    if (input == '?') {
        var input = 'introspect?';
    }
    var data = {'cellid':cellid, 'input':input};
    $.ajax({
            url:path,
            type:'POST',
            data:data,
            dataType:'json',
            success:self.evalSuccess});

    return;
}; 

Notebook.Async.evalSuccess = function(response) {
    var self = Notebook.Async;
    var t = Notebook.TreeBranch;
    var cellid = response.cellid;
    var incount = 'In[' + response.count + ']:';
    var outcount = 'Out[' + response.count + ']:';
    $('#'+cellid)[0].saved = true; //not evaluating
    //This is where numbering of cells could go.
    $('#'+cellid)[0].numberLabel(incount);
    var cellstyle = response.cellstyle;
    var content = response.content;
    t.spawnOutputCellNode(cellid, cellstyle, content, outcount);
    $('#'+cellid)[0].evalResult();
    Notebook.Save._save(self.evalSaveSuccess, self.evalSaveError);
};

Notebook.Async.evalError = function(response) {
};

Notebook.Async.evalSaveSuccess = function(response) {
};

Notebook.Async.evalSaveError = function(response) {
};


Notebook.Async.saveToDatabase = function(orderlist, cellsdata, success, error) {
    var path = BASE_URL+'save';
    var cells = JSON.stringify(cellsdata);
    var data = {'orderlist':orderlist, 'cellsdata':cells};
    $.ajax({
            url:path,
            type:'POST',
            data:data,
            dataType:'json',
            success:success,
            error:error});
};

Notebook.Async.deleteCells = function(mainid, ids) {
    var path = BASE_URL+'delete';
    var cellids = JSON.stringify(ids);
    var data = {'cellids':cellids};
    /*xxx: need to finish
    var d = a.doXHR(path, {
                    method:'post',
                    headers:{'Content-Type':'application/x-www-form-urlencoded'},
                    sendContent:data});
    var delback = b.partial($(mainid).deleteCallback, mainid)
    d.addCallbacks(delback, $(mainid).deleteErr);
    return d;
    */
};

Notebook.Async.changeNotebookTitle = function(title, success, error) {
    var path = BASE_URL+'change';
    var data = {'newtitle':title};
    $.ajax({
            url:path,
            type:'POST',
            data:data,
            dataType:'json',
            success:success,
            error:error});
};



/** completeName - for completing the name of a variable or function */
Notebook.Async.completeName = function(cellid, mode, input, success, error) {
    //request match from server
    // this ultimatly returns a list of 0 or more match possibilities
    var path = BASE_URL+'completer';
    var data = {'cellid':cellid, 'mode':mode, 'input':input};
    $.ajax({
            url:path,
            type:'POST',
            data:data,
            dataType:'json',
            success:success,
            error:error});
};

//$(document).ready(Notebook.Async.initialize);
Notebook.__init__.Async = function() {
    Notebook.Async.initialize();
};
