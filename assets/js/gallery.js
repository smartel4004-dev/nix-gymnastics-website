/* Gallery lightbox (PhotoSwipe 5). Without JS each thumbnail still links to the full photo. */
import PhotoSwipeLightbox from "../vendor/photoswipe/photoswipe-lightbox.esm.min.js";

var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

var lightbox = new PhotoSwipeLightbox({
  gallery: "[data-gallery]",
  children: "a",
  pswpModule: function () { return import("../vendor/photoswipe/photoswipe.esm.min.js"); },
  bgOpacity: 0.94,
  showHideAnimationType: reduceMotion ? "none" : "zoom",
  closeTitle: "Close (Esc)",
  arrowPrevTitle: "Previous photo",
  arrowNextTitle: "Next photo",
  zoomTitle: "Zoom",
  errorMsg: "This photo didn't load. Close and try again.",
  paddingFn: function (viewport) {
    return viewport.x < 700 ? { top: 56, bottom: 96, left: 0, right: 0 } : { top: 64, bottom: 96, left: 72, right: 72 };
  }
});

// Caption from each photo's alt text, announced as the slide changes
lightbox.on("uiRegister", function () {
  lightbox.pswp.ui.registerElement({
    name: "caption",
    order: 9,
    isButton: false,
    appendTo: "root",
    onInit: function (el, pswp) {
      el.setAttribute("aria-live", "polite");
      pswp.on("change", function () {
        var img = pswp.currSlide.data.element && pswp.currSlide.data.element.querySelector("img");
        el.textContent = img ? img.alt : "";
      });
    }
  });
});

lightbox.init();
