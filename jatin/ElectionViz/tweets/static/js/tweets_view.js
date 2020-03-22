// predeclared: tweetData, mapData, metric, setup
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
                    parsedData = parseTweetData(tweetData);
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

const parseTweetData = function(tweetData) {
    let parsed = {};
    
    for (let i = 0; i < tweetData.length; i++) {
        const district = parseInt(tweetData[i]['district']);
        const party = tweetData[i]['party'];
        const candidate = tweetData[i]['candidate'];
        const total_likes = parseInt(tweetData[i]['total_likes']);
        const num_tweets = parseInt(tweetData[i]['num_tweets']);
        const max_likes = parseInt(tweetData[i]['max_likes']);
        const tweet_text = tweetData[i]['tweet_text'];
        const first_name = tweetData[i]['first_name'];
        const last_name = tweetData[i]['last_name'];
        const tweet_date = tweetData[i]['tweet_date'];
        if (!(district in parsed)) {
            // initializes democrat and republican fields for the district
            parsed[district] = {};
            const parties = ['Democrat', 'Republican'];
            for (let j = 0; j < parties.length; j++) {
                const new_entry = {};
                new_entry['candidate'] = null;
                new_entry['total_likes'] = 0;
                new_entry['num_tweets'] = 0;
                new_entry['max_likes'] = 0;
                new_entry['tweet_text'] = null;
                new_entry['first_name'] = null;
                new_entry['last_name'] = null;
                new_entry['tweet_date'] = null;
                parsed[district][parties[j]] = new_entry;
            }
        }
        parsed[district][party]['candidate'] = candidate;
        parsed[district][party]['total_likes'] = total_likes;
        parsed[district][party]['num_tweets'] = num_tweets;
        parsed[district][party]['max_likes'] = max_likes;
        parsed[district][party]['tweet_text'] = tweet_text;
        parsed[district][party]['first_name'] = first_name;
        parsed[district][party]['last_name'] = last_name;
        parsed[district][party]['tweet_date'] = tweet_date;
    }
    return parsed;
};

// puts data in format DISTRICT => PARTY => [candidate, total_likes, num_tweets]
// easy for rendering
let parsedData = parseTweetData(tweetData);

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
    if (!(id in parsedData)) {
        return "No tweets"
    }
    const dem_count = parsedData[id]['Democrat']['num_tweets'];
    const dem_likes = parsedData[id]['Democrat']['total_likes'];
    const rep_count = parsedData[id]['Republican']['num_tweets'];
    const rep_likes = parsedData[id]['Republican']['total_likes'];
    let larger_party = 'Democrat';
    if (parsedData[id]['Republican'][metric] > parsedData[id]['Democrat'][metric]) {
        larger_party = 'Republican';
    }
    const pctg = Math.round(parsedData[id][larger_party][metric] / (parsedData[id]['Democrat'][metric] + parsedData[id]['Republican'][metric]) * 100 * 100) / 100;
    const most_liked_tweet = parsedData[id][larger_party]['tweet_text'];
    const num_likes = parsedData[id][larger_party]['max_likes'];
    const first_name = parsedData[id][larger_party]['first_name'];
    const last_name = parsedData[id][larger_party]['last_name'];
    const tweet_date = parsedData[id][larger_party]['tweet_date'];

    // format
    // pctg% <larger_party>
    // <dem_count> D, <rep_count> R
    // <dem_likes> likes, <rep_likes> likes
    // 
    // "<most_liked_tweet>"
    // - <first_name> <last_name>
    // <num_likes> likes
    // <tweet_date>
    return pctg.toString() + '% ' + larger_party + '\n' + dem_count.toString() + ' D, ' + rep_count.toString() + ' R\n' + dem_likes.toString() + ' &#x2665, ' + rep_likes.toString() + ' &#x2665\n\n"' + most_liked_tweet + '"\n- ' + first_name + ' ' + last_name + '\n' + num_likes.toString() + ' &#x2665\n' + tweet_date;
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
            hover_div.html(text)
                 .style("left", (d3.event.pageX + 10) + "px")
                 .style("top", (d3.event.pageY - 15) + "px");
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
    if (!(id in parsedData)) {
        return d3.rgb(0, 0, 0);
    }
    const district_data = parsedData[id];
    const ratio = district_data['Democrat'][metric] / (district_data['Democrat'][metric] + district_data['Republican'][metric])
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

