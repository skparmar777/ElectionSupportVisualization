// predeclared: tweetData, mapData, metric, setup, democrat_candidates, republican_candidates
// format of tweetData: DISTRICT -> PARTY -> CANDIDATE -> [total_likes, num_tweets, max_likes, tweet_text, first_name, last_name]
// console.log('tweetData: ', tweetData);
// console.log('mapData: ', mapData);
// console.log('metric: ', metric);

const reset = function() {
    chosen_democrats = [];
    chosen_republicans = [];
    opacity_dict = null;
}

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
                if (xhttp.readyState === 4 && xhttp.status === 200) {
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

const renameDropdown = function() {
    let newText = 'Tweets ';
    if (metric === 'total_likes') {
        newText = 'Likes ';
    }
    $("#tweet_vs_likes_button").text(newText);
};

// select2 library
$(document).ready(function() {
    // add all candidates
    for (let i = 0; i < democrat_candidates.length; i++) {
        $("#select2_candidate_picker").append('<option value="Democrat">' + democrat_candidates[i] + '</option>');
    }
    for (let i = 0; i < republican_candidates.length; i++) {
        $("#select2_candidate_picker").append('<option value="Democrat">' + republican_candidates[i] + '</option>');
    }

    $('#select2_candidate_picker').select2({ width: '100%' });
    $('#select2_candidate_picker').on("change", function(e) { 
        // callback
        updateCandidates();
     });
});

const is_democrat = function(candidate) {
    return democrat_candidates.includes(candidate);
}

const updateCandidates = function() {
    const objs = $('#select2_candidate_picker').select2('data');
    reset();
    for (let i = 0; i < objs.length; i++) {
        const candidate = objs[i]['text'];
        if (is_democrat(candidate)) {
            chosen_democrats.push(candidate);
        } else {
            chosen_republicans.push(candidate);
        }
    }

    if (chosen_republicans.length === 0 && chosen_democrats.length > 0) {
        assign_candidates_colors('Democrat', chosen_democrats);
    }
    else if (chosen_democrats.length === 0 && chosen_republicans.length > 0) {
        assign_candidates_colors('Republican', chosen_democrats);
    }
    colorMap();
}

// declare variables
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

const get_group_metric = function(id, party) {
    const district_data = tweetData[id];
    const dem_data = district_data['Democrat'];
    const rep_data = district_data['Republican'];
    if (party === 'Democrat') {
        if (chosen_democrats.length === 0) {
            return dem_data['combined'][metric];
        }
        let party_metric = 0;
        for (let i = 0; i < chosen_democrats.length; i++) {
            if (chosen_democrats[i] in dem_data) {
                party_metric += dem_data[chosen_democrats[i]][metric];
            }
        }
        return party_metric;
    }
    else {
        if (chosen_republicans.length === 0) {
            return rep_data['combined'][metric];
        }
        let party_metric = 0;
        for (let i = 0; i < chosen_republicans.length; i++) {
            if (chosen_republicans[i] in rep_data) {
                party_metric += rep_data[chosen_republicans[i]][metric];
            }
        }
        return party_metric;
    }
}

const get_group_data = function(isLarger, id, party, candidates) {
    const district_data = tweetData[id];
    let num_tweets = null;
    let total_likes = null;
    let most_liked_tweet = null;
    let num_likes = 0;
    let first_name = null;
    let last_name = null;
    let tweet_date = null;
    let date_descriptor = null;

    if (candidates.length === 0) {
        num_tweets = district_data[party]['combined']['num_tweets'];
        total_likes = district_data[party]['combined']['total_likes'];
        most_liked_tweet = district_data[party]['combined']['tweet_text'];
        num_likes = district_data[party]['combined']['max_likes'];
        first_name = district_data[party]['combined']['first_name']
        last_name = district_data[party]['combined']['last_name']
        tweet_date = district_data[party]['combined']['tweet_date']
        date_descriptor = district_data[party]['combined']['date_descriptor'];
    }
    else {
        for (let i = 0; i < candidates.length; i++) {
            if (candidates[i] in district_data[party]) {
                num_tweets += district_data[party][candidates[i]]['num_tweets'];
                total_likes += district_data[party][candidates[i]]['total_likes'];
                if (district_data[party][candidates[i]]['max_likes'] > num_likes) {
                    num_likes = district_data[party][candidates[i]]['max_likes'];
                    most_liked_tweet = district_data[party][candidates[i]]['tweet_text'];
                    first_name = district_data[party][candidates[i]]['first_name'];
                    last_name = district_data[party][candidates[i]]['last_name'];
                    tweet_date = district_data[party][candidates[i]]['tweet_date'];
                    date_descriptor = district_data[party][candidates[i]]['date_descriptor'];
                }
            }
        }
    }
    if (isLarger) {
        return [num_tweets, total_likes, most_liked_tweet, num_likes, first_name, last_name, tweet_date, date_descriptor];
    }
    return [num_tweets, total_likes]
}

const get_single_party_data = function(id, party, candidates) {
    const party_data = tweetData[id][party];
    let larger_group = null;
    let larger_symbol = null;
    let larger_group_metric = 0;
    let larger_group_tweets = null;
    let larger_group_likes = null;

    let smaller_group = null;
    let smaller_symbol = null;
    let smaller_group_metric = 0;
    let smaller_group_tweets = null;
    let smaller_group_likes = null;

    let most_liked_tweet = null;
    let num_likes = 0;
    let first_name = null;
    let last_name = null;
    let tweet_date = null;
    let date_descriptor = null;

    for (let i = 0; i < candidates.length; i++) {
        const cand = candidates[i];
        if (cand in party_data) {
            const cand_data = party_data[cand];
            if (cand_data[metric] > larger_group_metric) {
                smaller_group = larger_group;
                smaller_symbol = larger_symbol;
                smaller_group_metric = larger_group_metric;
                smaller_group_tweets = larger_group_tweets;
                smaller_group_likes = larger_group_likes;

                larger_group = cand;
                larger_symbol = cand;
                larger_group_metric = cand_data[metric];
                larger_group_tweets = cand_data['num_tweets'];
                larger_group_likes = cand_data['total_likes'];
            }
            else if (cand_data[metric] > smaller_group_metric) {
                smaller_group = cand;
                smaller_symbol = cand;
                smaller_group_metric = cand_data[metric];
                smaller_group_tweets = cand_data['num_tweets'];
                smaller_group_likes = cand_data['total_likes'];
            }

            if (cand_data['max_likes'] > num_likes) {
                num_likes = cand_data['max_likes'];
                most_liked_tweet = cand_data['tweet_text'];
                first_name = cand_data['first_name'];
                last_name = cand_data['last_name'];
                tweet_date = cand_data['tweet_date'];
                date_descriptor = cand_data['date_descriptor'];
            }
        }
    }
    return [larger_group, larger_symbol, larger_group_metric, larger_group_tweets, larger_group_likes, smaller_group, smaller_symbol, smaller_group_metric, smaller_group_tweets, smaller_group_likes, most_liked_tweet, num_likes, first_name, last_name, tweet_date, date_descriptor];
}

const construct_hover_text = function(id) {
    const district_data = tweetData[id];
    const dem_data = district_data['Democrat'];
    const rep_data = district_data['Republican'];
    if (dem_data['combined']['num_tweets'] + rep_data['combined']['num_tweets'] === 0) {
        // no tweets
        return null;
    }
    let larger_group = null;
    let larger_symbol = null;
    let larger_group_metric = null;
    let larger_group_tweets = null;
    let larger_group_likes = null;

    let smaller_group = null;
    let smaller_symbol = null;
    let smaller_group_metric = null;
    let smaller_group_tweets = null;
    let smaller_group_likes = null;

    // used for rendering tweet
    let most_liked_tweet = null;
    let num_likes = 0;
    let first_name = null;
    let last_name = null;
    let tweet_date = null;
    let date_descriptor = null;

    if ((chosen_democrats.length !== 0 && chosen_republicans.length !== 0) || (chosen_democrats.length + chosen_republicans.length === 0)) {
        // cross-party comparison using selected candidates (or all if lists are empty)
        let larger_group_candidates = null;
        let smaller_group_candidates = null;
        const dem_metric = get_group_metric(id, 'Democrat');
        const rep_metric = get_group_metric(id, 'Republican');
        if (dem_metric > rep_metric) {
            larger_group = 'Democrat';
            larger_symbol = 'D';
            larger_group_metric = dem_metric;
            larger_group_candidates = chosen_democrats;
            smaller_group = 'Republican';
            smaller_symbol = 'R';
            smaller_group_metric = rep_metric;
            smaller_group_candidates = chosen_republicans;
        }
        else {
            larger_group = 'Republican';
            larger_symbol = 'R';
            larger_group_metric = rep_metric;
            larger_group_candidates = chosen_republicans;
            smaller_group = 'Democrat';
            smaller_symbol = 'D';
            smaller_group_metric = dem_metric;
            smaller_group_candidates = chosen_democrats;
        }
        [larger_group_tweets, larger_group_likes, most_liked_tweet, num_likes, first_name, last_name, tweet_date, date_descriptor] = get_group_data(true, id, larger_group, larger_group_candidates);
        [smaller_group_tweets, smaller_group_likes] = get_group_data(false, id, smaller_group, smaller_group_candidates);
    }
    else if (chosen_democrats.length === 0) {
        [larger_group, larger_symbol, larger_group_metric, larger_group_tweets, larger_group_likes, smaller_group, smaller_symbol, smaller_group_metric, smaller_group_tweets, smaller_group_likes, most_liked_tweet, num_likes, first_name, last_name, tweet_date, date_descriptor] = get_single_party_data(id, 'Republican', chosen_republicans);
    }
    else {
        [larger_group, larger_symbol, larger_group_metric, larger_group_tweets, larger_group_likes, smaller_group, smaller_symbol, smaller_group_metric, smaller_group_tweets, smaller_group_likes, most_liked_tweet, num_likes, first_name, last_name, tweet_date, date_descriptor] = get_single_party_data(id, 'Democrat', chosen_democrats);
    }
    
    if (larger_group === null) {
        // no info for this district
        return null;
    }

    const pctg = Math.round(larger_group_metric / (larger_group_metric + smaller_group_metric) * 100 * 100) / 100;

    // format
    // Distric <id>
    // pctg% <larger_group>
    // <larger_group_metric> <metric_as_string>, <smaller_group_metric> <metric_as_string>
    // 
    // "<most_liked_tweet from larger_group>" 
    // - <first_name> <last_name>
    // <num_likes> likes
    // <tweet_date>

    let date_string = null;
    if (date_descriptor === 'exact') {
        date_string = tweet_date;
    }
    else {
        // don't show time as this is not an exact date
        const splits = tweet_date.split(' ');
        date_string = 'Week of ' + splits[0] + ' '  + splits[1]
    }

    let metric_as_string = '<i class="fab fa-twitter"></i>';
    if (metric === 'total_likes') {
        metric_as_string = '&#x2665'; // hex code for heart (likes)
    }

    let smaller_group_metric_string = ', ' + smaller_group_metric.toString() + ' ' + metric_as_string + ' ' + smaller_symbol;
    if (smaller_symbol === null) {
        // happens when only one candidate is picked
        smaller_group_metric_string = '';
    }

    return '<u><strong>Distric ' + id.toString() + '</strong></u>\n' +
            pctg.toString() + '% ' + larger_group + '\n' +
            larger_group_metric.toString() + ' ' + metric_as_string + ' ' + larger_symbol + smaller_group_metric_string + '\n' +
            '\n' +
            '"' + most_liked_tweet  + '"\n- ' +
            first_name + ' ' + last_name + '\n' +
            num_likes.toString() + ' &#x2665\n' +
            date_string;
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
            if (opacity_dict !== null) {
                d3.select(this).transition()
                    .duration('50')
                    .attr('opacity', opacity_dict[d.properties['DISTRICT']]);
            }
            else {
                d3.select(this).transition()
                    .duration('50')
                    .attr('opacity', '1');
            }
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

const drColorScale = d3.scale.quantize()
                            .domain([0, 1.0])
                            .range(combinedList);

const blueCandidateColors = ['rgb(0, 63, 92)', 'rgb(122, 81, 149)', 'rgb(239, 86, 117)', 'rgb(255, 166, 0)'];
let cand_to_color = null;
let opacity_dict = null;

const assign_candidates_colors = function(party, candidates) {
    // assume party is democrat for now
    cand_to_color = {};
    opacity_dict = {};
    for (let i = 0; i < candidates.length; i++) {
        cand_to_color[candidates[i]] = blueCandidateColors[i];
    }
}

const rColorScale = d3.scale.quantize()
                            .domain([0, 1.0])
                            .range(redList);

const color_picker_single_party = function(id, party, candidates) {
    // chooses a color based on the candidates in a single party
    if (candidates.length === 1) {
        // color according to party
        if (party === 'Democrat') {
            return drColorScale(0.75);
        }
        else {
            return drColorScale(0.25);
        }
    }
    const district_data = tweetData[id];
    let party_total = 0;
    let party_largest = 0;
    let largest_cand = null;
    for (let i = 0; i < candidates.length; i++) {
        if (candidates[i] in district_data[party]) {
            const cand_metric = district_data[party][candidates[i]][metric];
            if (cand_metric > party_largest) {
                party_largest = cand_metric;
                largest_cand = candidates[i];
            }
            party_total += cand_metric;
        }
    }
    if (party_total === 0) {
        return d3.rgb(0, 0, 0);
    }

    opacity_dict[id] = party_largest / party_total;
    return cand_to_color[largest_cand];
}

const color_picker = function(id) {
    if (!(id in tweetData)) {
        return d3.rgb(0, 0, 0);
    }
    const district_data = tweetData[id];
    let ratio = null;
    if (chosen_democrats.length + chosen_republicans.length == 0) {
        // use all by default
        ratio = district_data['Democrat']['combined'][metric] / (district_data['Democrat']['combined'][metric] + district_data['Republican']['combined'][metric])
    }
    else if (chosen_democrats.length === 0) {
        // candidates of only republican party are chosen
        return color_picker_single_party(id, 'Republican', chosen_republicans);
    }
    else if (chosen_republicans.length === 0) {
        // candidates of only democrat are chosen
        return color_picker_single_party(id, 'Democrat', chosen_democrats);
    }
    else {
        let dem_total = 0;
        let rep_total = 0;
        for (let i = 0; i < chosen_democrats.length; i++) {
            if (chosen_democrats[i] in district_data['Democrat']) {
                dem_total += district_data['Democrat'][chosen_democrats[i]][metric];
            }
        }
        for (let i = 0; i < chosen_republicans.length; i++) {
            if (chosen_republicans[i] in district_data['Republican']) {
                rep_total += district_data['Republican'][chosen_republicans[i]][metric];
            }
        }
        ratio = dem_total / (dem_total + rep_total);
    }
    // lower the ratio, reder the color
    // higher the ratio, bluer the color
    return drColorScale(ratio);
}

const colorMap = function() {
    mapLayer.selectAll('path')
        .style('fill', function (d) {
            // console.log(d);
            const color = color_picker(d.properties['DISTRICT']);
            if (opacity_dict !== null) {
                d3.select(this).transition()
                                .duration('50')
                                .attr('opacity', opacity_dict[d.properties['DISTRICT']]);
            }
            else {
                d3.select(this).transition()
                                .duration('50')
                                .attr('opacity', 1);
            }
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

