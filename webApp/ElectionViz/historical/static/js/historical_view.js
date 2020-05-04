// predeclared: HISTORICAL_DATA, MAP_DATA, YEAR
// format of HISTORICAL_DATA: YEAR -> DISTRICT -> PARTY -> CANDIDATE -> VOTES

// define a function on strings to turn "COOK COUNTY" into "Cook County"
String.prototype.toProperCase = function () {
    return this.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
};

const all_years = Object.keys(HISTORICAL_DATA);
for (let i = 0; i < all_years.length; i++) {
    const new_a = `<a class='dropdown-item' onclick='YEAR = ${all_years[i]}; colorMap(); renameDropdown();'>${all_years[i]}</a>`;
    $(new_a).appendTo('.dropdown-menu');
}

const renameDropdown = function() {
    $("#year_button").text(YEAR);
};

renameDropdown();

// SVG
const width = 1200;
const height = 500*2;

const projection = d3.geo.mercator()
                            .scale(4000)
                            .center([-99, 39])
                            .translate([width / 2 - 700, height / 2 + 25*1]);

const path = d3.geo.path()
                    .projection(projection);

const svg = d3.select('svg')
                .attr('width', width)
                .attr('height', height);

const legendLayer = svg.append('g')
                        .classed('map-layer', true);

const mapLayer = svg.append('g')
                    .classed('map-layer', true);

const hover_div = d3.select("body").append("div")
                                    .attr("class", "hover-text")
                                    .style("opacity", 0);

// red colors, most red to least red
const redList = ['rgb(135, 0, 23)', 'rgb(179, 0, 21)', 'rgb(215, 0, 16)', 'rgb(237, 48, 56)', 'rgb(250, 91, 97)', 'rgb(250, 134, 136)']

// blue colors, least blue to most blue
const blueList = ['rgb(188, 210, 232)', 'rgb(145, 186, 214)', 'rgb(115, 165, 198)', 'rgb(82, 138, 174)', 'rgb(46, 89, 132)', 'rgb(30, 63, 102)']

const combinedList = redList.concat(blueList);

const drColorScale = d3.scale.quantize()
                            .domain([0, 1.0])
                            .range(combinedList);

const get_symbol = function(string) {
    if (string === 'Republican') {
        return 'R';
    }
    else if (string === 'Democrat') {
        return 'D';
    }
    return string;
}

const metric_as_string = function() {
    return '<i class="fas fa-vote-yea"></i>';
}

const construct_hover_text = function(district, name) {
    /**  FORMAT:
        County: <name>
        pctg% <larger_group>
        <larger_group_metric> <larger_group_symbol> <metric_as_string>, <smaller_group_metric> <smaller_group_symbol> <metric_as_string>
    */
    const data = HISTORICAL_DATA[YEAR][district];
    const dvalues = $.map(data['Democrat'], function(value, key) { return value });
    const dkeys = $.map(data['Democrat'], function(value, key) { return key });
    const rvalues = $.map(data['Republican'], function(value, key) { return value });
    const rkeys = $.map(data['Republican'], function(value, key) { return key });

    let larger = null;
    let larger_c = null;
    let smaller = null;
    let smaller_c = null;
    if (dvalues[0] > rvalues[0]) {
        larger = 'Democrat';
        larger_c = dkeys[0];
        smaller = 'Republican';
        smaller_c = rkeys[0];
    }
    else {
        larger = 'Republican';
        larger_c = rkeys[0];
        smaller = 'Democrat';
        smaller_c = dkeys[0];
    }
    const pctg = (100 * data[larger][larger_c] / (data[larger][larger_c] + data[smaller][smaller_c])).toFixed(2);
    const mas = metric_as_string();
    
   const string = `County: ${name.toProperCase()}\n \
                     ${pctg}% ${larger}\n \
                     ${data[larger][larger_c]} ${get_symbol(larger)} ${mas}, ${data[smaller][smaller_c]} ${get_symbol(smaller)} ${mas}\n`;
    return string;
}

// functions
const displayBaseMap = function () {
    // this is a global declared in the html
    const features = MAP_DATA.features;

    // title
    mapLayer.append("text")
            .classed("text", true)
            .attr("x", (width / 2))
            .attr("y", 60)
            .attr("text-anchor", "middle")
            .style("font-size", "30px")
            .style("font-family", "Arial")
            .text("Illinois Counties");


    mapLayer.selectAll('path')
        .data(features)
        .enter().append('path')
        .attr('d', path)
        .attr('vector-effect', 'non-scaling-stroke')

        //Our new hover effects
        .on('mouseover', function (d, i) {
            d3.select(this).transition()
                 .duration('50')
                 .attr('opacity', '.85');
            hover_div.transition()
                 .duration(50)
                 .style("opacity", 1);
            const text = construct_hover_text(d.properties['DISTRICT'], d.properties['COUNTY_NAM']);
            if (text !== null) {
                hover_div.html(text)
                            .style("left", (d3.event.pageX + 10) + "px")
                            .style("top", (d3.event.pageY - 15) + "px");
            }
            else {
                hover_div.transition()
                            .duration('50')
                            .style("opacity", 0);
            }
       })
       .on('mouseout', function (d, i) {
            d3.select(this).transition()
                .duration('50')
                .attr('opacity', '1');
            hover_div.transition()
                 .duration('50')
                 .style("opacity", 0);
       });

    console.log("done rendering base map!");
}

const colorMap = function() {
    mapLayer.selectAll('path')
        .style('fill', function (d) {
            const data = HISTORICAL_DATA[YEAR][d.properties['DISTRICT']];
            const dvalues = $.map(data['Democrat'], function(value, key) { return value });
            const rvalues = $.map(data['Republican'], function(value, key) { return value });
            return drColorScale(dvalues[0] / (dvalues[0] + rvalues[0]));
        });
}

const createLegend = function() {
    legendLayer.select('g').remove();
    const legend = legendLayer.append("g")
                                .attr("class", "quantize")
                                .attr("transform", "translate(" + width / 9 + "," + height / 2 + ")")
                                .style('font-family', 'Garamond')
                                .style('font-size', '16')
                                .style('position', 'absolute');

    const quant = d3.scale.ordinal()
                            .domain(domain)
                            .range(range);
    
    let domain = []; // names of the legend boxes
    let range = []; // colors of the legend boxes
    for (let i = 0; i < redColor.length; i++) {

    }

    const legendQuant = d3.legend.color()
                                    .title("Color Legend")
                                    .labelFormat(d3.format('.0f'))
                                    .scale(quant);
}

displayBaseMap();
colorMap();

