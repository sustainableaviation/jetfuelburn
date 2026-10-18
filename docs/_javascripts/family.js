// On the local preview, Library and API point at the two dev servers.
// Anywhere else they keep the public addresses in the header markup.
(function () {
  if (location.port !== "8010" && location.port !== "3000") return;
  var base = location.protocol + "//" + location.hostname;
  var map = {
    library: base + ":8010/",
    api: base + ":3000/introduction",
  };
  document.querySelectorAll(".jfb-family [data-family]").forEach(function (item) {
    var href = map[item.getAttribute("data-family")];
    if (href && item.tagName === "A") item.setAttribute("href", href);
  });
})();
