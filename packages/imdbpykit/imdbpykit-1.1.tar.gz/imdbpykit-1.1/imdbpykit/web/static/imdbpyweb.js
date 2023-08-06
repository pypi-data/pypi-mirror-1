function _disappear(obj, mode, changeImg) {
  if (document.getElementById(obj).style.visibility == "hidden") {
    document.getElementById(obj).style.visibility = "visible";
    document.getElementById(obj).style.display = mode;
    if (changeImg == 1) {
      document.getElementById("img" + obj).src = "/static/less.png";
    }
  } else {
    document.getElementById(obj).style.visibility = "hidden";
    document.getElementById(obj).style.display = "none";
    if (changeImg == 1) {
      document.getElementById("img" + obj).src = "/static/more.png";
    }
  }
}

function disappear(obj) {
  _disappear(obj, "inline", 1);
}

function disappearBlock(obj) {
  _disappear(obj, "block", 0);
}


function doAll(what) {
  var disp = "inline";
  if (what == "hidden") {
    disp = "none";
  }
  var items = document.getElementsByTagName("span");
  for (var j = 0; j < items.length; j++) {
    node = items[j];
    if (node.getAttribute("class") == "hideable") {
      node.style.display = disp;
      node.style.visibility = what;
    }
  }
  var items = document.getElementsByTagName("div");
  for (var j = 0; j < items.length; j++) {
    node = items[j];
    if (node.getAttribute("class") == "hideable") {
      node.style.display = disp;
      node.style.visibility = what;
    }
  }
  var items = document.getElementsByTagName("img");
  for (var j = 0; j < items.length; j++) {
    node = items[j];
    if (node.getAttribute("class") == "mglass") {
      if (what == "hidden") {
        node.src = "/static/more.png";
      } else {
        node.src = "/static/less.png";
      }
    }
  }
}
