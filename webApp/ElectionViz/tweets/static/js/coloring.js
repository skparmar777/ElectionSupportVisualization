// red colors, most red to least red
const redList = ['rgb(135, 0, 23)', 'rgb(179, 0, 21)', 'rgb(215, 0, 16)', 'rgb(237, 48, 56)', 'rgb(250, 91, 97)', 'rgb(250, 134, 136)']

// blue colors, least blue to most blue
const blueList = ['rgb(188, 210, 232)', 'rgb(145, 186, 214)', 'rgb(115, 165, 198)', 'rgb(82, 138, 174)', 'rgb(46, 89, 132)', 'rgb(30, 63, 102)']

const combinedList = redList.concat(blueList);

const drColorScale = d3.scale.quantize()
                            .domain([0, 1.0])
                            .range(combinedList);

const rColorScale = d3.scale.quantize()
                        .domain([0, 1.0])
                .range(redList);

const blueCandidateColors = ['rgb(0, 63, 92)', 'rgb(122, 81, 149)', 'rgb(239, 86, 117)', 'rgb(255, 166, 0)'];
let cand_to_color = {'Democrat': {}, 'Republican': {}};
// let opacity_dict = null;

const set_cand_to_color = function(democrats, republicans) {
    for (let i = 0; i < democrats.length; i++) {
        cand_to_color['Democrat'][democrats[i]] = blueCandidateColors[i];
    }
    // NEED TO ADD REPUBLICAN-ish colors, right now using blue
    for (let i = 0; i < republicans.length; i++) {
        cand_to_color['Republican'][republicans[i]] = blueCandidateColors[i];
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
        else if (candidates.length === 1) {
            // only looking at one candidate
            if (party === 'Democrat') {
                return [drColorScale(0.75), 1.0]
            }
            else {
                return [drColorScale(0.25), 1.0]
            }
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
            // special case, can't just sum
            const dem_value = TWEETS_INTERFACE.get_average_sentiment_data(district, 'Democrat', democrats, polarity)['avg_sentiment'];
            const rep_value = TWEETS_INTERFACE.get_average_sentiment_data(district, 'Republican', republicans, polarity)['avg_sentiment'];
            if (dem_value === null && rep_value === null) {
                return [d3.rgb(0, 0, 0), 1.0];
            }
            else if (dem_value === null) {
                return [drColorScale(0), 1.0]
            }
            else if (rep_value === null) {
                return [drColorScale(1), 1.0]
            }
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
}
