var allImagesCount, imagesLoadedCount;

var pdfText = {
  counter: 0,
  list: [],
  url_list: [],
  work: function() {
    if (pdfText.list.length < 1) {
      return false;
    }
    pdfText.list[pdfText.counter].children[0].style.opcity = 0;
    $.ajax({
      method: "POST",
      async: true,
      url: "/get_pdf_content",
      data: {
        file_path: pdfText.url_list[pdfText.counter].replace('media/', '')
      },
      success: function(data) {
        if (data.status) {
          pdfText.list[pdfText.counter].children[0].innerHTML = data.message;
          pdfText.list[pdfText.counter].children[0].classList.add('opac_lighter');
        } else {
          console.log('data, error: ', data);
        }
        if (pdfText.counter < pdfText.list.length - 1) {
          pdfText.counter++;
          pdfText.work();
        }
      },
      error: function(data, err) {
        console.log('data, error: ', data, err);
      }
    });
  }
};

var makeContainerElement = function(url, height, kind, text) {

  var beginname = url.lastIndexOf('/') + 1;

  var atag = document.createElement('a');
  atag.href = '/' + url;
  atag.setAttribute('download', url.slice(beginname));
  atag.title = specificTranslations.ClickDownload + ' ' + url.slice(beginname);
  atag.style.height = height;

  if (kind == 'img') {

    var imgtag = document.createElement(kind);
    imgtag.src = '/' + url;
    imgtag.addEventListener('load', function() {
      this.classList.add('lighter');
      this.parentNode.style.height = 'auto';
    });

    atag.appendChild(imgtag);

  } else if (kind == 'pdf') {

    var spantag = document.createElement('span');
    spantag.innerHTML = '<div class="text"></div><i class="fa fa-file-' + kind + '-o" aria-hidden="true"></i>';
    spantag.style.fontSize = '2vw';
    pdfText.list.push(spantag);
    pdfText.url_list.push(url);
    spantag.classList.add('lighter');

    atag.appendChild(spantag);
    atag.style.height = 'auto';

  } else {

    var spantag = document.createElement('span');
    if (text && text.length > 0) {
      spantag.innerHTML = '<div class="text">' + text + '</div><i class="fa fa-file-' + kind + '-o" aria-hidden="true"></i>';
    } else {
      spantag.innerHTML = '<i class="fa fa-file-' + kind + '-o" aria-hidden="true"></i>';
    }
    spantag.style.fontSize = '2vw';
    spantag.classList.add('lighter');

    atag.appendChild(spantag);
    atag.style.height = 'auto';

  }

  var element = document.createElement('div');
  element.classList.add('element');
  element.appendChild(atag);
  var wrap = document.createElement('div');
  wrap.appendChild(element);

  return wrap;
};

var removeInfo = function(gone) {
  var el = document.getElementById('pos_' + gone).parentNode;
  delete photos[gone];
  var plusRequired = (el == document.getElementsByClassName('divs-striped')[0]);
  var elParent = el.parentNode;
  elParent.removeChild(el);
  var delTrashParent = document.getElementsByClassName('delediline')[0];
  if (plusRequired) {
    var addPlus = document.createElement('a');
    addPlus.href = '/create_information/';
    addPlus.title = specificTranslations.AddNewInfo;
    addPlus.classList.add('btn_inTabRow');
    addPlus.innerHTML = '<i class="fa fa-plus-square-o" aria-hidden="true"></i>';
    delTrashParent.insertBefore(addPlus, delTrashParent.children[0]);
  }
  if (Object.keys(photos).length < 2) {
    if (delTrashParent.children.length == 3) {
      delTrashParent.removeChild(delTrashParent.children[1])
    }
  }
};

var deleteInfo = function(todel) {
  $.confirm({
    title: '',
    //title: specificTranslations.Confirm + '!',
    content: specificTranslations.WantDeleteInfo + '?',
    buttons: {
      confirm: {
        text: specificTranslations.BtnConfirm,
        action: function() {
          $.post('/delete_information', {
            pk: todel
          }, function(data, status) {
            console.log('data, status: ', data, status);
            if (data.status) {
              removeInfo(data.gone);
              console.log(data.status + ' ' + data.message + ' ' + data.gone);
            } else {
              $.alert('ooops, error while deleting record ... ' + data.message);
            }
          });
        }
      },
      cancel: {
        text: specificTranslations.BtnCancel
      }
    }
  });
};

document.addEventListener('DOMContentLoaded', function() {
  allImagesCount = imagesLoadedCount = 0;
  var imagecontainers = document.getElementsByClassName('info_images_container');
  var itemscontainer = document.getElementById('items_container');
  var pk = 3;
  if (photos[pk]) {
    console.log('photos[pk].length: ', photos[pk]);
    for (var j = 0; j < photos[pk].length; j++) {
      var beginrealurl = photos[pk][j].indexOf('media/infophotos/');
      var useurl = photos[pk][j].slice(beginrealurl);
      if (photos[pk][j].toLowerCase().indexOf('.jpg') != -1 || photos[pk][j].toLowerCase().indexOf('.jpeg') != -1 || photos[pk][j].toLowerCase().indexOf('.png') != -1) {
        allImagesCount++;

        var ar = photos[pk][j].slice(0, photos[pk][j].indexOf('_'))

        if (window.innerWidth > 767) {

          var aheight = (ar != 'noimage') ? (40 / ar) + 'vw' : 40 + 'vw';

        } else {

          var aheight = (ar != 'noimage') ? ((window.innerWidth - 72) / ar) + 'px' : 'calc(100vw - 72px)';

        }

        itemscontainer.appendChild(makeContainerElement(useurl, aheight, 'img'));

      } else {
        var aheight = (window.innerWidth > 767) ? 40 + 'vw' : 'calc(100vw - 72px)';

        var ext = 'text';
        if (photos[pk][j].toLowerCase().indexOf('.pdf') != -1) {
          ext = 'pdf';
        } else if (photos[pk][j].toLowerCase().indexOf('.xlsx') != -1 || photos[pk][j].toLowerCase().indexOf('.ods') != -1) {
          ext = 'excel';
        } else if (photos[pk][j].toLowerCase().indexOf('.docx') != -1 || photos[pk][j].toLowerCase().indexOf('.odt') != -1) {
          ext = 'word';
        }

        itemscontainer.appendChild(makeContainerElement(useurl, aheight, ext, text_dict[pk][j]));

      }
    }
  }
  //console.log('pdfText.list: ', pdfText.list);
  //pdfText.work();
});
