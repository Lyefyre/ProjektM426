Dropzone.autoDiscover = false; // otherwise will be initialized twice

var buttonsSH;
var myFileTypes = {
  'text/plain': '/static/images/svg-fa/text-o.svg',
  'application/pdf': '/static/images/svg-fa/pdf-o.svg',
  'excel': '/static/images/svg-fa/excel-o.svg',
  'word': '/static/images/svg-fa/word-o.svg',
  'work': function(fobj, ftype, ustr) {
    if (ustr.indexOf('.pdf') != -1) {
      fobj.tnclass = true;
      return this['application/pdf'];
    } else if (ustr.indexOf('.txt') != -1) {
      fobj.tnclass = true;
      return this['text/plain'];
    } else if (ustr.indexOf('.xlsx') != -1 || ustr.indexOf('.ods') != -1) {
      fobj.tnclass = true;
      return this['excel'];
    } else if (ustr.indexOf('.docx') != -1 || ustr.indexOf('.odt') != -1) {
      fobj.tnclass = true;
      return this['word'];
    }
    console.log('ft :', ftype);
    if (ftype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || ftype == 'application/vnd.oasis.opendocument.spreadsheet') {
      ftype = 'excel';
    } else if (ftype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || ftype == 'application/vnd.oasis.opendocument.text') {
      ftype = 'word';
    }
    if (this[ftype]) {
      fobj.tnclass = true;
      return this[ftype];
    }
    return false;
  }
};
document.addEventListener('DOMContentLoaded', function() {
  var el_status = document.getElementById('id_status');
  el_status.parentNode.classList.add('overlap');
  el_status.addEventListener('change', function(e) {
    e.target.blur();
  }, false);
  var el_infopk = document.getElementById('id_infopk');
  var el_title = document.getElementById('id_title');
  if (!el_infopk) {
    /* form in create mode */
    el_title.value = document.getElementById('id_text').value = '';
    el_title.focus();
    el_title.addEventListener('keyup', function(e) {
      document.getElementById('btn_add_files').style.display = document.getElementById('btn_save_changes').style.display = (e.target.value.length > 0) ? 'inline-block' : 'none';
    }, false);
    document.getElementById('btn_add_files').addEventListener('click', function() {
      document.getElementById('id_listorimages').value = 1;
      document.getElementById('info-form').submit();
    }, false);
    return;
  } else {
    /* form in edit mode */
    buttonsSH = {
      usedDone: true,
      usedBack: true,
      showDone: function() {
        if (this.usedDone) {
          console.log('28 ', this);
          document.getElementById('btn_save_changes').style.display = 'inline-block'
          this.usedDone = false;
        }
      },
      hideBack: function() {
        if (this.usedBack) {
          console.log('28 ', this);
          document.getElementById('btn_revert_changes').style.display = 'none'
          this.usedBack = false;
        }
      },
    };
    el_title.addEventListener('keyup', function() {
      buttonsSH.showDone();
    }, false);
    document.getElementById('id_text').addEventListener('keyup', function() {
      buttonsSH.showDone();
    }, false);
    document.getElementById('id_status').addEventListener('change', function() {
      buttonsSH.showDone();
    }, false);
    var addphotos = document.getElementById('add-photos');
    addphotos.style.display = 'flex';
    addphotos.action = '/ajax-infoupload/' + el_infopk.value + '/';
  }

  var myDropzoneOptions = {
    acceptedFiles: 'text/plain, application/pdf, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.oasis.opendocument.spreadsheet, application/vnd.openxmlformats-officedocument.wordprocessingml.document, application/vnd.oasis.opendocument.text, image/jpeg, image/png',
    init: function() {
      this.on("addedfile", function(file) {
        var url = myFileTypes.work(file, file.type, '');
        if (url) {
          myDropzone.emit("thumbnail", file, url);
        }
        if (file.tnclass) {
          file.previewElement.children[0].children[0].classList.add('icon');
        }
      });
    },
    renameFile: function(file) {
      var oldName = String(file.name).toLowerCase().replace(/ /g, '_').replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue');
      var newName = oldName.replace(/[^A-Za-z0-9._]/g, '');
      console.log('renameFile: ', newName);
      return newName;
    },
    dictFileTooBig: specificTranslations.FileSize + ' {{filesize}} MB.<br>' + specificTranslations.MaxFileSize + ' {{maxFilesize}} MB.',
    dictInvalidFileType: specificTranslations.InvalidFileType + '<br>' + specificTranslations.OkFileTypeMsg + '<br>JPG PNG Text PDF Excel Word',
    maxFilesize: 5,
    addRemoveLinks: true,
    dictRemoveFile: '<i title="' + specificTranslations.RemoveFile + '" class="fa fa-trash-o" aria-hidden="true" data-dz-remove></i>',
    clickable: true,
    success: function(file) {
      console.log('succ');
      file_up_names.push(file.name);
      buttonsSH.showDone();
      buttonsSH.hideBack();
    },
    error: function(file, err) {
      file.previewElement.parentNode.removeChild(file.previewElement);
      $.confirm({
        useBootstrap: false,
        boxWidth: '100%',
        title: '',
        //autoClose: 'confirm|2400',
        content: err,
        buttons: {
          confirm: {
            text: specificTranslations.BtnConfirm
          }
        }
      });
    },
    removedfile: function(file) {
      var lastslash = file.name.lastIndexOf('/') + 1;
      var ix_in_names = file_up_names.indexOf(file.name.slice(lastslash));
      $.confirm({
        useBootstrap: false,
        boxWidth: '100%',
        title: '',
        content: specificTranslations.WantDeleteFile + '?<br>' + file.name.slice(lastslash),
        buttons: {
          confirm: {
            text: specificTranslations.BtnConfirm,
            action: function() {
              if (ix_in_names != -1) {
                $.ajax({
                  method: "POST",
                  async: true,
                  url: "/delete_info_file",
                  data: {
                    file_name: file_up_names[ix_in_names],
                    file_dir: el_infopk.value
                  },
                  success: function(data) {
                    console.log('data: ', data);
                    if (data.status) {
                      file_up_names.splice(ix_in_names, 1);
                      toRemove = file.previewElement;
                      toRemove.parentNode.removeChild(toRemove);
                      buttonsSH.showDone();
                      buttonsSH.hideBack();
                    } else {
                      $.alert('ooops, error while deleting file ... ' + data.message);
                    }
                  },
                  error: function(data, err) {
                    console.log('data, error: ', data, err);
                  }
                });
              }
            }
          },
          cancel: {
            text: specificTranslations.BtnCancel
          }
        }
      });
    }
  };
  var myDropzone = new Dropzone(".dropzone", myDropzoneOptions);
  var file_up_names = [];
  for (var i = 0; i < image_urls.length; i++) {
    if (image_urls[i].indexOf('.DS_Store') == -1) {
      var beginrealurl = image_urls[i].indexOf('media/infophotos/');
      var mockFile = image_urls[i].slice(beginrealurl);
      var lastslash = mockFile.lastIndexOf('/') + 1;
      console.log('mockFile: ', mockFile);
      var metafile = {
        name: mockFile.slice(lastslash),
        size: 12345,
        accepted: true,
        kind: 'image'
      };
      var url = '/' + mockFile;
      var iconurl = myFileTypes.work(metafile, '', url);
      file_up_names.push(mockFile.slice(lastslash));
      myDropzone.emit("addedfile", metafile);
      myDropzone.emit("thumbnail", metafile, (iconurl) ? iconurl : url);
    }
  }
  var positioner = document.getElementsByClassName('positioner')[0];
  positioner.scrollIntoView({
    block: "start",
    behavior: "smooth"
  });
  var remlk = document.getElementsByClassName('dz-remove');
  for (var i = 0; i < remlk.length; i++) {
    remlk[i].removeAttribute('href');
  }
});