// Renders Plotly figures emitted by markdown-exec blocks as inert JSON in a
// data attribute. Inline <script> tags in page content are unreliable under
// instant navigation, so figures are drawn from here on every page load.
document$.subscribe(function() {
  document.querySelectorAll("div.plotly-figure").forEach(function(el) {
    var spec = JSON.parse(el.dataset.fig)
    Plotly.newPlot(el.querySelector("div.plotly-figure-target"), spec.data, spec.layout, { responsive: true })
  })
})
