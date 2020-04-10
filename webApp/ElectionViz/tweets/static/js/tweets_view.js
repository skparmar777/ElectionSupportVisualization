// predeclared: TWEETS_INTERFACE, MAP_DATA, METRIC, SETUP, DEMOCRAT_CANDIDATES, REPUBLICAN_CANDIDATES
// format of tweetData: DISTRICT -> PARTY -> CANDIDATE -> POLARITY -> [total_likes, num_tweets, avg_sentiment, tweet]
// tweet keys: likes, username, tweet_text, tweet_date, date_descriptor
// there are also 'combined' values at the CANDIDATE and PARTY level

const reset = function() {
    chosen_democrats = [];
    chosen_republicans = [];
    opacity_dict = null;
}

const renameDropdown = function() {
    let newText = 'Tweets ';
    if (METRIC === 'total_likes') {
        newText = 'Likes ';
    }
    else if (METRIC === 'avg_sentiment') {
        newText = 'Sentiment ';
    }
    $("#tweet_vs_likes_button").text(newText);
};

const updateCandidates = function() {
    // called whenever something is selected
    const objs = $('#select2_candidate_picker').select2('data');
    reset();
    for (let i = 0; i < objs.length; i++) {
        const candidate = objs[i]['text'];
        if (DEMOCRAT_CANDIDATES.includes(candidate)) {
            chosen_democrats.push(candidate);
        }
        else {
            chosen_republicans.push(candidate);
        }
    }
    colorMap();
}

// declare variables
color_interface = new ColorInterface(DEMOCRAT_CANDIDATES, REPUBLICAN_CANDIDATES);

let chosen_democrats = [];
let chosen_republicans = [];

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

const get_symbol = function(string) {
    if (string === 'Republican') {
        return 'R';
    }
    else if (string === 'Democrat') {
        return 'D';
    }
    return string;
}

const metric_as_string = function(metric) {
    if (metric === 'total_likes') {
        return '&#x2665';
    }
    else if (metric == 'num_tweets') {
        return '<i class="fab fa-twitter"></i>';
    }
    return '<i class="fas fa-poll"></i>';
}

const construct_hover_text = function(district) {
    /**  FORMAT:
        Distric <id>
        pctg% <larger_group>
        <larger_group_metric> <larger_group_symbol> <metric_as_string>, <smaller_group_metric> <smaller_group_symbol> <metric_as_string>

        "<most_liked_tweet from larger_group>" 
        - username
        <likes> likes, <sentiment> sentiment
        <tweet_date>
    */
   const data = TWEETS_INTERFACE.get_hover_text_info(district, chosen_democrats, chosen_republicans, METRIC, POLARITY);
   if (data === null) {
       return null;
   }
   const pctg = (100 * data['larger_group_metric'] / (data['larger_group_metric'] + data['smaller_group_metric'])).toFixed(2);
   if (METRIC === 'avg_sentiment') {
       // push back to between -1 and 1 for displaying
       data['larger_group_metric'] = (data['larger_group_metric'] * 2 - 1).toFixed(2);
       data['smaller_group_metric'] = (data['smaller_group_metric'] * 2 - 1).toFixed(2);
   }
   const sentiment = data['sentiment'].toFixed(2);
   const mas = metric_as_string(METRIC);
   let date_string = data['tweet_date'];
   if (data['date_descriptor'] !== 'exact') {
        const splits = date_string.split(' ');
        date_string = 'Week of ' + splits[0] + ' '  + splits[1]
   }
    
   const string = `District ${district}\n \
                     ${pctg}% ${data['larger_group']}\n \
                     ${data['larger_group_metric']} ${get_symbol(data['larger_group'])} ${mas}, ${data['smaller_group_metric']} ${get_symbol(data['smaller_group'])} ${mas}\n \
                     \n \
                     "${data['tweet_text']}"\n \
                     - ${data['username']}\n \
                     ${data['likes']} ${metric_as_string('total_likes')}, ${sentiment} ${metric_as_string('avg_sentiment')} \n \
                     ${date_string}\n`;
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
            .text("Illinois Congressional Districts");


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
            const text = construct_hover_text(d.properties['DISTRICT']);
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
            const color = color_interface.chose_color(d.properties['DISTRICT'], chosen_democrats, chosen_republicans, METRIC, POLARITY);
            // d3.select(this).transition()
            //                 .duration('50')
            //                 .attr('opacity', opacity_dict[d.properties['DISTRICT']]);
            return color;
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
