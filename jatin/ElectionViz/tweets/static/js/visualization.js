console.log('data: ', data);
console.log('map_json: ', map_json);

// declare variables
const width = 1200;
const height = 500*2;

const projection = d3.geo.mercator()
                            .scale(4000)
                            .center([-99, 39])
                            .translate([width / 2 - 700, height / 2 + 25*1]);

const path = d3.geo.path()
                    .projection(projection);

// Set svg width & height
const svg = d3.select('svg')
                .attr('width', width)
                .attr('height', height);

let legendLayer = svg.append('g')
                        .classed('map-layer', true);

const mapLayer = svg.append('g')
                    .classed('map-layer', true);

const displayBaseMap = function (mapData, mapLayer, path, width, height) {
    let features = mapData.features;
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

displayBaseMap(map_json, mapLayer, path, width, height);

