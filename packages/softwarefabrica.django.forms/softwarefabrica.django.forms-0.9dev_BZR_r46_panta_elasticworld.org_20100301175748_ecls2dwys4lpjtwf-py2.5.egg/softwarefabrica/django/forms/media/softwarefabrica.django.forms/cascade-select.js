/*!
 * cascade-select.js JavaScript
 *
 * Implements "cascaded SELECTs", form SELECT elements which change
 * contents through AJAX when the contents in a master SELECT changes.
 *
 * This module requires jQuery 1.3.2
 *
 * Copyright (C) 2009-2010 Marco Pantaleoni. All rights reserved.
 */

/*
 * triggerChange() triggers a 'change' event on the given SELECT
 * element, performing debouncing (collapsing multiple 'change' events),
 * and eventually waiting for settling of other SELECT widgets
 * upon this one is dependent (in other words, where the given one
 * is a slave).
 */
function triggerChange($select, select, selector) {
  if (select.changing) {
    //console.log(selector + " debounced. Skipping.");
    return true;
  }
  if (select.master_select !== undefined) {
    if (select.master_select.setup_complete) {
      //console.log(selector + ".master is SETTLED");
    } else {
      //console.log(selector + ".master is PENDING...");
      var f = function () {
        return triggerChange($select, select, selector);
      }
      var t = setTimeout(f, 100);
      return false;
    }
  }

  //console.log(selector + " <- change [triggerChange - IMMEDIATE]");
  select.changing = true;
  $select.trigger("change");
  return true;
}

var _on_master_select_helper = function(eventObject, url,
                                        master_selector, $master_select, master_select,
                                        master_app, master_model,
                                        slave_selector, $slave_select, slave_select,
                                        slave_app, slave_model, slave_pivot,
                                        callbackOnSetup, callbackOnCascade)
{
  //var master_text = $master_select.find('option:selected').text();
  //console.log("on_master_select(" + master_select.name + ", text:" + master_text + ")");
  //console.log("model:" + master_model + " value:" + master_select.value + "  index:" + master_select.selectedIndex);

  var old_slave_selection = slave_select.value;
  slave_select.in_cascading_update = true;
  slave_select.old_selection = old_slave_selection;

  //$slave_select.find('option').remove();
  $slave_select.children().remove();
  slave_select.add(new Option("Loading ...", ""), document.all ? 0 : null);
  //slave_select.disabled = true;

  $.get(url,
    { 'master_app'  : master_app,
      'master_model': master_model,
      'master_id'   : master_select.value,
      'slave_app'   : slave_app,
      'slave_model' : slave_model,
      'slave_pivot' : slave_pivot
    },
    function(data) {
      if (data) {
        //$slave_select.find('option').remove();
        $slave_select.children().remove();
        if (data.length != 1) {
          var opt = new Option("---------", "");
          slave_select.add(opt, document.all ? 0 : null);
          opt.selected = true;
        }
        for (var i in data) {
          var opt = new Option(data[i].text, data[i].pk);
          slave_select.add(opt, document.all ? 0 : null);
          if ((data.length == 1) || (data[i].pk == old_slave_selection)) {
            opt.selected = true;
          }
        }
        if (data.length > 1) {
          //slave_select.disabled = false;
        }
        //console.log(slave_selector + " <- change [slave]");
        //$slave_select.trigger("change");
        triggerChange($slave_select, slave_select, slave_selector);

        slave_select.in_cascading_update = false;
        if (callbackOnCascade !== undefined) {
          callbackOnCascade(slave_select, master_select);
        }
        if ((callbackOnSetup !== undefined) && (! master_select.setup_complete)) {
          master_select.setup_complete = true;
          callbackOnSetup(master_select);
        }
        master_select.setup_complete = true;
        master_select.changing = false;
      }
    },
    "json");
}

function setupCascadedSelect(url,
                             master_selector, master_app, master_model,
                             slave_selector, slave_app, slave_model, slave_pivot,
                             callbackOnSetup, callbackOnCascade)
{
  //console.log("setupCascadedSelect(" + master_model + ", " + slave_model + ")");
  var $master_select = $(master_selector);
  var master_select = $master_select.get(0);

  master_select.setup_complete = false;

  var $slave_select = $(slave_selector);
  var slave_select  = $slave_select.get(0);

  master_select.slave_select = slave_select;
  slave_select.master_select = master_select;

  var on_master_select = function(eventObject) {
    _on_master_select_helper(eventObject, url,
                             master_selector, $master_select, master_select,
                             master_app, master_model,
                             slave_selector, $slave_select, slave_select,
                             slave_app, slave_model, slave_pivot,
                             callbackOnSetup, callbackOnCascade);
  }
  $master_select.change( on_master_select );

  /*
   * We now trigger a 'change' event on the master SELECT, to force an update
   * on the slave.
   * We must pay attention to dependency problems though.
   * If the master SELECT is in turn a slave for some other SELECT, than
   * we should wait that its master is completely settled.
   */
  //console.log(master_selector + " <- change [master]");
  //$master_select.trigger("change");
  triggerChange($master_select, master_select, master_selector);
}
