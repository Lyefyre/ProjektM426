var display;
var spellIt = function(i) {
  display.innerHTML += i + '<br>';
};


var contentSwitch = function(name) {
  console.log(name);
  var allPages = document.querySelectorAll('.display');

  for (var i = 0; i < allPages.length; i++) {
    console.log(allPages[i]);
    if (allPages[i].id != name.replace(/ /g, '_')) {
      allPages[i].style.display = 'none';
    } else {
      allPages[i].style.display = 'flex';
    }
  }

  document.getElementById('subject').innerHTML = 'you are at "' + name + '" view.';

};

document.addEventListener('DOMContentLoaded', function() {

  menu = document.getElementById('menu');

  for (var i = 0; i < menu.children.length; i++) {
    menu.children[i].addEventListener('click', function(e) {
      contentSwitch(e.target.innerHTML);
    }, false);
  }

}, false);