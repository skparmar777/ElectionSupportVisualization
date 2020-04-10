// Load map data
d3.json('data/illinois.json', function (error, mapData) {

    var width = 1200;
    var height = 500*2;

    var projection = d3.geo.mercator()
        .scale(4000)
        .center([-99, 39])
        .translate([width / 2 - 700, height / 2 + 25*1]);

    var path = d3.geo.path()
                        .projection(projection);

    // Set svg width & height
    var svg = d3.select('svg')
        .attr('width', width)
        .attr('height', height);

    var mapLayer = svg.append('g')
                        .classed('map-layer', true);
    // var legendLayer = svg.append('g')
    //                     .classed('map-layer', true);

    displayBaseMap(mapData, mapLayer, path, width, height);
});

const displayBaseMap = function (mapData, mapLayer, path, width, height) {

    var features = mapData.features;
    console.log("loaded map data");

    // title
    mapLayer.append("text")
            .classed("text", true)
            .attr("x", (width / 2))
            .attr("y", 60)
            .attr("text-anchor", "middle")
            .style("font-size", "30px")
            .style("font-family", "Arial")
            .text("Illinois Congressional Districts");


    mapLayer.selectAll('path')
        .data(features)
        .enter().append('path')
        .attr('d', path)
        .attr('vector-effect', 'non-scaling-stroke');

    console.log("done rendering base map!");
}
