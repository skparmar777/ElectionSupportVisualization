// red colors, most red to least red
const redList = ['rgb(135, 0, 23)', 'rgb(179, 0, 21)', 'rgb(215, 0, 16)', 'rgb(237, 48, 56)', 'rgb(250, 91, 97)', 'rgb(250, 134, 136)']

// blue colors, least blue to most blue
const blueList = ['rgb(188, 210, 232)', 'rgb(145, 186, 214)', 'rgb(115, 165, 198)', 'rgb(82, 138, 174)', 'rgb(46, 89, 132)', 'rgb(30, 63, 102)']

const combinedList = redList.concat(blueList);

const drColorScale = d3.scale.quantize()
                            .domain([0, 1.0])
                            .range(combinedList);


const redCandidateColors = ['rgb(255, 40, 0)', 'rgb(66, 13, 9)', 'rgb(141, 2, 31)', 'rgb(180, 55, 87)'];
const blueCandidateColors = ['rgb(42, 82, 190)', 'rgb(122, 81, 149)', 'rgb(10, 186, 181)', 'rgb(93, 138, 168)'];
let cand_to_color = {'Democrat': {}, 'Republican': {}};

const set_cand_to_color = function(democrats, republicans) {
    for (let i = 0; i < democrats.length; i++) {
        cand_to_color['Democrat'][democrats[i]] = blueCandidateColors[i];
    }
    for (let i = 0; i < republicans.length; i++) {
        cand_to_color['Republican'][republicans[i]] = redCandidateColors[i];
    }
}

class ColorInterface {
    constructor(democrats, republicans) {
        set_cand_to_color(democrats, republicans);
    }

    /**
     * Choose the display when only candidates from a single party are chosen
     * Return: color and opacity
     */
    choose_color_sp(district, party, candidates, metric, polarity) {
        const vals = TWEETS_INTERFACE.get_values(district, party, candidates, metric, polarity);
        if (vals === null) {
            return [d3.rgb(0, 0, 0), 1.0];
        }
        if (metric === 'avg_sentiment') {
            const party_res = TWEETS_INTERFACE.get_average_sentiment_data(district, party, candidates, polarity);
            let total_metric = (party_res['avg_sentiment'] + 1)/2; // normalize to 0-1
            const max_c = party_res['max_candidate'];
            let max_contrib = party_res['contribution']; // percentage of total_metric from max candidate
            let max_c_tmp = max_contrib * total_metric; // normalized importance
            if (metric === "avg_sentiment") {
                for (let i = 0; i < candidates.length; i++) {
                    if (!(candidates[i] in vals)) {
                        total_metric += 0.5; // assume neutral
                    }
                }
            }
            max_contrib = max_c_tmp / total_metric;
            return [cand_to_color[party][max_c], max_contrib];
        }
        let max_val = null;
        let max_c = null;
        let total_val = null;
        for (let k in vals) {
            if (max_val === null || max_val < vals[k]) {
                max_val = vals[k];
                max_c = k;
                total_val += vals[k];
            }
        }
        // set the opacity to be higher if the max_c contributes more to the total
        return [cand_to_color[party][max_c], max_val / total_val];
    }

    /**
     * Choose the display when only candidates from a single party are chosen
     * Return: color and opacity
     */
    choose_color_cp(district, democrats, republicans, metric, polarity) {
        if (metric == 'avg_sentiment') {
            // special case, can't just sum so need to use special function to aggregate
            let dem_value = TWEETS_INTERFACE.get_average_sentiment_data(district, 'Democrat', democrats, polarity)['avg_sentiment'];
            let rep_value = TWEETS_INTERFACE.get_average_sentiment_data(district, 'Republican', republicans, polarity)['avg_sentiment'];
            if (dem_value === null && rep_value === null) {
                return [d3.rgb(0, 0, 0), 1.0];
            }
            else if (dem_value === null) {
                dem_value = 0; // assume neutral support
            }
            else if (rep_value === null) {
                rep_value = 0; // assume neutral support
            }
            dem_value = (1 + dem_value) / 2; // normalize between 0-1
            rep_value = (1 + rep_value) / 2; // normalize between 0-1
            return [drColorScale(dem_value / (dem_value + rep_value)), 1.0]
        }
        const dem_values = TWEETS_INTERFACE.get_values(district, 'Democrat', democrats, metric, polarity);
        const rep_values = TWEETS_INTERFACE.get_values(district, 'Republican', republicans, metric, polarity);
        if (dem_values === null && rep_values === null) {
            return [d3.rgb(0, 0, 0), 1.0];
        }
        else if (dem_values === null) {
            return [drColorScale(0), 1.0];
        }
        else if (rep_values === null) {
            return [drColorScale(1), 1.0];
        }
        let dem_total = 0;
        for (let k in dem_values) {
            dem_total += dem_values[k];
        }
        let rep_total = 0;
        for (let k in rep_values) {
            rep_total += rep_values[k];
        }
        return [drColorScale(dem_total / (dem_total + rep_total)), 1.0]; // more blue, the higher dems are, and vice versa
    }

    /**
     * Determines the color and opacity
     */
    choose_color(district, democrats, republicans, metric, polarity) {
        if (democrats.length === 0 && republicans.length !== 0) {
            return this.choose_color_sp(district, 'Republican', republicans, metric, polarity);
        }
        else if (democrats.length !== 0 && republicans.length === 0) {
            return this.choose_color_sp(district, 'Democrat', democrats, metric, polarity);
        }
        else {
            return this.choose_color_cp(district, democrats, republicans, metric, polarity);
        }
    }

    /**
     * Used to create the legend
     * Returns domain, range where domain is a list of labels for legend boxes, and range is the corresponding color
     */
    find_legend_domain_range(democrats, republicans) {
        if (democrats.length === 0 && republicans.length !== 0) {
            const domain = Object.keys(cand_to_color['Republican']);
            let range = [];
            for (let i = 0; i < domain.length; i++) {
                range.push(cand_to_color['Republican'][domain[i]]);
            }
            return [domain, range];
        }
        else if (democrats.length !== 0 && republicans.length === 0) {
            const domain = Object.keys(cand_to_color['Democrat']);
            let range = [];
            for (let i = 0; i < domain.length; i++) {
                range.push(cand_to_color['Democrat'][domain[i]]);
            }
            return [domain, range];
        }
        else {
            const domain = ["100% Republican", "80% Republican", "60% Republican", "60% Democrat", "80% Democrat", "100% Democrat"];
            const range = [drColorScale(0.0), drColorScale(0.2), drColorScale(0.4), drColorScale(0.6), drColorScale(0.8), drColorScale(1.0)];
            return [domain, range];
        }
    }
}
