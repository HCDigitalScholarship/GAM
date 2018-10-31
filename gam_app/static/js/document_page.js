$(document).ready(function () {
    var viewer = OpenSeadragon({
      id: "openseadragon1",
      zoomInButton: "zoom-in",
      zoomOutButton: "zoom-out",
      homeButton: "home",
      fullPageButton: "full-page",
      previousButton: "previous",
      rotateRightButton: "right-rotate",
      rotateLeftButton: "left-rotate",
      /* This value comes from an inline script in the template. */
      tileSources: dziFile,
      showRotationControl: true,
    });

    var viewer = OpenSeadragon({
      id: "openseadragon2",
      crossOriginPolicy: 'Anonymous',
      collectionMode: true,
      collectionRows: 1,
      showNavigationControl: false
    });

    $(".helpme").select2({
        ajax: {
        url: '/en/autocompletar',
        dataType: 'json'
        },
        val: ["1"], // I think this is supposed to refer to the ID of the option in the list?
    });
    var images = [];
    for (var i = 0; i < srcs.length; i++) {
        viewer.addTiledImage({
          tileSource: srcs[i],
          success: function (event) {
            images.push(event.item);
          }
        });
    }

    addLinkOverlays()
});




function addLinkOverlays() {
  for (var i = 0; i < images.length; i++) {
    addOneLinkOverlay(images[i], items[i][1]);
  }
  viewer.viewport.goHome();
}


function addOneLinkOverlay(image, link) {
    var imageRect = image.getBounds();
    var rect = new OpenSeadragon.Rect(imageRect.x, imageRect.y, 0.05, 0.05);

    var buttonElement = document.createElement("a");
    var imgElement = document.createElement("img");
    imgElement.src = editButtonURL;
    imgElement.href = link;
    buttonElement.appendChild(imgElement);
    //buttonElement.className = "highlight";
    viewer.addOverlay(buttonElement, rect, OpenSeadragon.OverlayPlacement.CENTER);

    viewer.addViewerInputHook({
        hooks: [{
            tracker: "viewer",
            handler: "clickHandler",
            hookHandler: function (event) {
              event.preventDefaultAction = true;
              var pos = viewer.viewport.viewerElementToViewportCoordinates(event.position);
              if (isPointInsideRect(pos, rect.clone())) {
                  window.location.href = link;
              }
            },
        }]
    });
}


function isPointInsideRect(point, rect) {
    return point.x > rect.x && point.x < rect.x + rect.width && point.y > rect.y &&
           point.y < rect.y + rect.height;
}

function areAllFullyLoaded() {
  var tiledImage;
  var count = viewer.world.getItemCount();
  for (var i = 0; i < count; i++) {
    tiledImage = viewer.world.getItemAt(i);
    if (!tiledImage.getFullyLoaded()) {
      return false;
    }
  }
  return true;
}

var isFullyLoaded = false;

viewer.world.addHandler('add-item', function(event) {
  var tiledImage = event.item;
  tiledImage.addHandler('fully-loaded-change', function() {
    var newFullyLoaded = areAllFullyLoaded();
    if (newFullyLoaded !== isFullyLoaded) {
      isFullyLoaded = newFullyLoaded;
      // Raise event
      if (isFullyLoaded) {
         addLinkOverlays();
       }
    }
  });
}
