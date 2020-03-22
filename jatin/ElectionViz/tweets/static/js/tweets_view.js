// predeclared: tweetData, mapData, metric, setup
// format of tweetData: DISTRICT -> PARTY -> CANDIDATE -> [total_likes, num_tweets, max_likes, tweet_text, first_name, last_name]
// console.log('tweetData: ', tweetData);
// console.log('mapData: ', mapData);
// console.log('metric: ', metric);

// date range library
$(function() {
    var start = moment().subtract(6, 'days');
    var end = moment();

    function callback(start, end) {
        $('#reportrange span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
        if (setup != 1) {
            // POST request with new payload
            var xhttp = new XMLHttpRequest();
            const params = "daterange=" + $('#reportrange span').text();
            xhttp.onreadystatechange = function() {
                if (xhttp.readyState == 4 && xhttp.status == 200) {
                    // render the new data
                    tweetData = JSON.parse(xhttp.responseText);
                    colorMap();
                }
            };
            xhttp.open("POST", window.location.href, false);
            xhttp.send(params);
        }
        setup = 0;
    }

    $('#reportrange').daterangepicker({
        startDate: start,
        endDate: end,
        ranges: {
           'Today': [moment(), moment()],
           'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
           'Last 7 Days': [moment().subtract(6, 'days'), moment()],
        }
    }, callback);

    callback(start, end);

});

// declare variables
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

// const legendLayer = svg.append('g')
//                         .classed('map-layer', true);

const mapLayer = svg.append('g')
                    .classed('map-layer', true);

const hover_div = d3.select("body").append("div")
                                    .attr("class", "hover-text")
                                    .style("opacity", 0);

const construct_hover_text = function(id) {
    const dem_data = tweetData[id]['Democrat'];
    const rep_data = tweetData[id]['Republican']
    if (dem_data['combined']['num_tweets'] + rep_data['combined']['num_tweets'] == 0) {
        // no tweets
        return null;
    }
    const dem_count = dem_data['combined']['num_tweets'];
    const dem_likes = dem_data['combined']['total_likes'];
    const rep_count = rep_data['combined']['num_tweets'];
    const rep_likes = rep_data['combined']['total_likes'];
    let larger_party = 'Democrat';
    if (rep_data['combined'][metric] > dem_data['combined'][metric]) {
        larger_party = 'Republican';
    }
    const pctg = Math.round(tweetData[id][larger_party]['combined'][metric] / (dem_data['combined'][metric] + rep_data['combined'][metric]) * 100 * 100) / 100;
    const most_liked_tweet = tweetData[id][larger_party]['combined']['tweet_text'];
    const num_likes = tweetData[id][larger_party]['combined']['max_likes'];
    const first_name = tweetData[id][larger_party]['combined']['first_name'];
    const last_name = tweetData[id][larger_party]['combined']['last_name'];
    const tweet_date = tweetData[id][larger_party]['combined']['tweet_date'];

    // format
    // Distric <id>: pctg% <larger_party>
    // <dem_count> D, <rep_count> R
    // <dem_likes> likes, <rep_likes> likes
    // 
    // "<most_liked_tweet>"
    // - <first_name> <last_name>
    // <num_likes> likes
    // <tweet_date>

    let date_string = null;
    if (tweetData[id][larger_party]['combined']['date_descriptor'] === 'exact') {
        date_string = tweet_date;
    }
    else {
        // don't show time as this is not an exact date
        const splits = tweet_date.split(' ');
        date_string = 'Week of ' + splits[0] + ' '  + splits[1]
    }
    return '<u><strong>Distric ' + id.toString() + '</strong></u>\n' + pctg.toString() + '% ' + larger_party + '\n' + dem_count.toString() + ' D, ' + rep_count.toString() + ' R\n' + dem_likes.toString() + ' &#x2665, ' + rep_likes.toString() + ' &#x2665\n\n"' + most_liked_tweet + '"\n- ' + first_name + ' ' + last_name + '\n' + num_likes.toString() + ' &#x2665\n' + date_string;
}

// functions
const displayBaseMap = function () {
    // this is a global declared in the html
    const features = mapData.features;

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

// red colors, most red to least red
const redList = ['rgb(135, 0, 23)', 'rgb(179, 0, 21)', 'rgb(215, 0, 16)', 'rgb(237, 48, 56)', 'rgb(250, 91, 97)', 'rgb(250, 134, 136)']

// blue colors, least blue to most blue
const blueList = ['rgb(188, 210, 232)', 'rgb(145, 186, 214)', 'rgb(115, 165, 198)', 'rgb(82, 138, 174)', 'rgb(46, 89, 132)', 'rgb(30, 63, 102)']

const combinedList = redList.concat(blueList);

hueScale = d3.scale.quantize()
                            .domain([0, 1.0])
                            .range(combinedList);
            
const color_picker = function(id) {
    if (!(id in tweetData)) {
        return d3.rgb(0, 0, 0);
    }
    const district_data = tweetData[id];
    const ratio = district_data['Democrat']['combined'][metric] / (district_data['Democrat']['combined'][metric] + district_data['Republican']['combined'][metric])
    // lower the ratio, reder the color
    // higher the ratio, bluer the color
    return hueScale(ratio);
}

const colorMap = function() {
    mapLayer.selectAll('path')
        .style('fill', function (d) {
            // console.log(d);
            return color_picker(d.properties['DISTRICT']);
        });
}

const renameDropdown = function() {
    let newText = 'Tweets';
    if (metric === 'total_likes') {
        newText = 'Likes';
    }
    $("#tweet_vs_likes_button").text(newText);
};

displayBaseMap();
colorMap();

