// Tweaks for integrating datatables + bootstrap

/* Default class modification */
$.extend($.fn.dataTableExt.oStdClasses, {
  "sWrapper": "dataTables_wrapper form-inline"
});

/* API method to get paging information */
$.fn.dataTableExt.oApi.fnPagingInfo = function(oSettings) {
  return {
    "iStart":         oSettings._iDisplayStart,
    "iEnd":           oSettings.fnDisplayEnd(),
    "iLength":        oSettings._iDisplayLength,
    "iTotal":         oSettings.fnRecordsTotal(),
    "iFilteredTotal": oSettings.fnRecordsDisplay(),
    "iPage":          Math.ceil(oSettings._iDisplayStart / oSettings._iDisplayLength),
    "iTotalPages":    Math.ceil(oSettings.fnRecordsDisplay() / oSettings._iDisplayLength)
  };
}

/* Bootstrap style pagination control */
$.extend($.fn.dataTableExt.oPagination, {
  "bootstrap": {
    "fnInit": function(oSettings, nPaging, fnDraw) {
      var oLang = oSettings.oLanguage.oPaginate;
      var fnClickHandler = function(e) {
        e.preventDefault();
        if (oSettings.oApi._fnPageChange(oSettings, e.data.action)) {
          fnDraw(oSettings);
        }
      };

      $(nPaging).addClass('pagination').append(
          '<ul>' +
              '<li class="prev disabled"><a href="#">&larr; ' + oLang.sPrevious + '</a></li>' +
              '<li class="next disabled"><a href="#">' + oLang.sNext + ' &rarr; </a></li>' +
              '</ul>'
      );
      var els = $('a', nPaging);
      $(els[0]).bind('click.DT', { action: "previous" }, fnClickHandler);
      $(els[1]).bind('click.DT', { action: "next" }, fnClickHandler);
    },

    "fnUpdate": function(oSettings, fnDraw) {
      var iListLength = 5;
      var oPaging = oSettings.oInstance.fnPagingInfo();
      var an = oSettings.aanFeatures.p;
      var i, j, sClass, iStart, iEnd, iHalf = Math.floor(iListLength / 2);

      if (oPaging.iTotalPages < iListLength) {
        iStart = 1;
        iEnd = oPaging.iTotalPages;
      }
      else if (oPaging.iPage <= iHalf) {
        iStart = 1;
        iEnd = iListLength;
      } else if (oPaging.iPage >= (oPaging.iTotalPages - iHalf)) {
        iStart = oPaging.iTotalPages - iListLength + 1;
        iEnd = oPaging.iTotalPages;
      } else {
        iStart = oPaging.iPage - iHalf + 1;
        iEnd = iStart + iListLength - 1;
      }

      for (i = 0, iLen = an.length; i < iLen; i++) {
        // Remove the middle elements
        $('li:gt(0)', an[i]).filter(':not(:last)').remove();

        // Add the new list items and their event handlers
        for (j = iStart; j <= iEnd; j++) {
          sClass = (j == oPaging.iPage + 1) ? 'class="active"' : '';
          $('<li ' + sClass + '><a href="#">' + j + '</a></li>')
              .insertBefore($('li:last', an[i])[0])
              .bind('click', function(e) {
                e.preventDefault();
                oSettings._iDisplayStart = (parseInt($('a', this).text(), 10) - 1) * oPaging.iLength;
                fnDraw(oSettings);
              });
        }

        // Add / remove disabled classes from the static elements
        if (oPaging.iPage === 0) {
          $('li:first', an[i]).addClass('disabled');
        } else {
          $('li:first', an[i]).removeClass('disabled');
        }

        if (oPaging.iPage === oPaging.iTotalPages - 1 || oPaging.iTotalPages === 0) {
          $('li:last', an[i]).addClass('disabled');
        } else {
          $('li:last', an[i]).removeClass('disabled');
        }
      }
    }
  }
});

/* Table initialisation */
$(document).ready(function() {
  $('#example').dataTable({
    "sDom":            "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
    "sPaginationType": "bootstrap",
    "oLanguage":       {
      "sLengthMenu": "_MENU_ records per page"
    }
  });
});


// live search
$(document).ready(function() {
  $("#search-box").keyup(function() {
    var q = $(this).val();
    if (q == '') {
      $("#live-search-results").html("").hide();
    } else {
      $.ajax({
        type:    "GET",
        url:     "/search/live?q=" + q,
        cache:   false,
        success: function(html) {
          if (html) {
            $("#live-search-results").html(html).show();
          } else {
            $("#live-search-results").html("").hide();
          }
        }
      });
    }
    return false;
  });

});


// Various widgets
$(function() {

  $('.dropdown-toggle').dropdown();

  $('.chzn-select').chosen({allow_single_deselect: true});

  $('.tagbox').tagBox();

  $('.collapsable').collapse({
    show: function() {
      this.animate({
        opacity: 'toggle',
        height:  'toggle'
      }, 150);
    },

    hide: function() {
      this.animate({
        opacity: 'toggle',
        height:  'toggle'
      }, 150);
    }
  });
});

/*
 $(function() {
 $('#fileupload').fileupload({
 dataType: 'json',

 done: function(e, data) {
 $.each(data.result, function(index, file) {
 $('<p/>').text(file.name).appendTo(document.body);
 });
 },

 add: function(e, data) {
 $.each(data.result, function(index, file) {
 $('<p/>').text(file.name).appendTo(document.body);
 });
 }
 });
 });

 */

/* ==========================================================
 * bootstrap-placeholder.js v2.0.0
 * http://jasny.github.com/bootstrap/javascript.html#placeholder
 *
 * Based on work by Daniel Stocks (http://webcloud.se)
 * ==========================================================
 * Copyright 2012 Jasny BV.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================== */

/* TODO: turn this into a proper bootstrap plugin */
$(function() {
  $('*[data-fileupload]').each(function() {
    var container = $(this);
    var input = $(this).find(':file');
    var name = input.attr('name');
    if (input.length == 0) return;

    var preview = $(this).find('.fileupload-preview');
    if (preview.css('display') != 'inline' && preview.css('height') != 'none') {
      preview.css('line-height', preview.css('height'));
    }

    var remove = $(this).find('*[data-dismiss="fileupload"]');

    var hidden_input = $(this).find(':hidden[name="' + name + '"]');
    if (!hidden_input.length) {
      hidden_input = $('<input type="hidden" />');
      container.prepend(hidden_input);
    }

    var type = container.attr('data-fileupload') == "image" ? "image" : "file";

    input.change(function(e) {
      hidden_input.val('');
      hidden_input.attr('name', '')
      input.attr('name', name);

      var file = e.target.files[0];

      if (type == "image" && preview.length
          && (typeof file.type !== "undefined" ? file.type.match('image.*') : file.name.match('\\.(gif|png|jpg)$'))
          && typeof FileReader !== "undefined") {
        var reader = new FileReader();

        reader.onload = function(e) {
          preview.html('<img src="' + e.target.result + '" ' + (preview.css('max-height') != 'none' ? 'style="max-height: ' + preview.css('max-height') + ';"' : '') + ' />');
          container.addClass('fileupload-exists').removeClass('fileupload-new');
        }

        reader.readAsDataURL(file);
      } else {
        preview.html(escape(file.name));
        container.addClass('fileupload-exists').removeClass('fileupload-new');
      }
    });

    remove.click(function() {
      hidden_input.val('');
      hidden_input.attr('name', name);
      input.attr('name', '');

      preview.html('');
      container.addClass('fileupload-new').removeClass('fileupload-exists');

      return false;
    });
  })
});