
class TweetsInterface {
    constructor(tweetsData) {
      this.tweetsData = tweetsData;
    }

    set_data(tweetsData) {
        this.tweetsData = tweetsData;
    }

    get_values(district, party, candidates, metric, polarity) {
        /**
         * inputs self explanatory
         * if length of candidates is 0, uses the 'combined' field
         * 
         * returns a dict with key : candidate, value : metric value for given polarity
         */
        // console.assert(metric in ['total_likes', 'num_tweets', 'avg_sentiment']);
        // console.assert(polarity in ['P', 'N', 'combined']);
        const ddict = this.tweetsData[district][party];
        if (ddict === 'null') {
            return null;
        }
        if (candidates.length == 0) {
            if (ddict['combined'] === 'null') {
                return null;
            }
            if (!(polarity in ddict['combined']) || ddict['combined'][polarity] === 'null') {
                return null;
            }
            return {'combined': ddict['combined'][polarity][metric]};
        }
        let ret = {};
        for (let i = 0; i < candidates.length; i++) {
            if (candidates[i] === 'combined' || !(candidates[i] in ddict) || !(polarity in ddict[candidates[i]]) || ddict[candidates[i]][polarity] === 'null') {
                continue;
            }
            ret[candidates[i]] = ddict[candidates[i]][polarity][metric];
        }
        if (Object.keys(ret).length === 0) {
            return null;
        }
        return ret;
    }

    get_tweet(district, party, candidate, polarity) {
         /**
         * inputs self explanatory
         * if candidate is null, uses the 'combined' field
         * 
         * returns a dict with key : candidate, value : metric value for given polarity
         */
        // assert(polarity in ['P', 'N', 'combined']);
        const ddict = this.tweetsData[district][party];
        if (ddict === 'null') {
            return null;
        }
        if (candidate === null) {
            if (!(polarity in ddict['combined']) || ddict['combined'][polarity] === 'null') {
                return null;
            }
            return ddict['combined'][polarity]['tweet'];
        }
        if (!(polarity in ddict[candidate])) {
            return null;
        }
        return ddict[candidate][polarity]['tweet'];
    }

    get_average_sentiment_data(district, party, candidates, polarity) {
        /**
         * Performs the proper aggregation for sentiment on a party and subset of candidates
         * Normalizes the sentiment to 0-1 so ratios can be constructed
         * 
         * Returns the average sentiment, the max contributor, and their fractional contribution
         */
        const avg_sentiment_vals = this.get_values(district, party, candidates, 'avg_sentiment', polarity);
        if (avg_sentiment_vals === null) {
            return {
                'avg_sentiment': null,
                'max_candidate': null,
                'contribution': null
            };
        }
        const num_tweet_vals = this.get_values(district, party, candidates, 'num_tweets', polarity);
        let total = 0;
        let total_tweets = 0;
        let max_v = 0;
        let max_c = null;
        for (let k in avg_sentiment_vals) {
            const norm = ((avg_sentiment_vals[k] + 1) / 2) * num_tweet_vals[k];
            total += norm; // normalizes to 0-1 for easy ratio-making
            total_tweets += num_tweet_vals[k];
            if (norm > max_v) {
                max_v = norm;
                max_c = k;
            }
        }
        return {
            'avg_sentiment': (total / total_tweets) * 2 - 1, // scale back to -1 to 1
            'max_candidate': max_c,
            'contribution': max_v / total // percentage of total
        };
    }

    get_hover_text_info_sp(district, party, candidates, metric, polarity) {
        /**
         * Called by get_hover_text_info
         */
        const vals = this.get_values(district, party, candidates, metric, polarity);
        if (vals === null) {
            return null;
        }
        let max_c = null;
        let max_contrib = null;
        let total_metric = 0;
        if (metric === 'avg_sentiment') {
            const party_res = this.get_average_sentiment_data(district, party, candidates, polarity);
            total_metric = (party_res['avg_sentiment'] + 1)/2; // normalize to 0-1
            max_c = party_res['max_candidate'];
            max_contrib = party_res['contribution']; // percentage of total_metric from max candidate
            let max_c_tmp = max_contrib * total_metric; // normalized importance
            if (metric === "avg_sentiment") {
                for (let i = 0; i < candidates.length; i++) {
                    if (!(candidates[i] in vals)) {
                        total_metric += 0.5; // assume neutral
                    }
                }
            }
            max_contrib = max_c_tmp / total_metric;
        }
        else {
            for (let k in vals) {
                if (max_contrib === null || vals[k] > max_contrib) {
                    max_contrib = vals[k];
                    max_c = k;
                }
                total_metric += vals[k];
            }
        }
        if (max_c === null) {
            return null;
        }
        let larger_group_metric = max_contrib;
        let smaller_group_metric = total_metric - max_contrib;
        if (metric === 'avg_sentiment') {
            // scale back to -1 to 1
            larger_group_metric = (2 * max_contrib * total_metric) - 1;
            smaller_group_metric = 2 * (total_metric - max_contrib * total_metric) - 1;
        }
        if (polarity === 'combined') {
            // this tells the get_tweet function to get the largest contributor
            // but only using the most positive contributor
            polarity = 'P';
        }
        let tweet = this.get_tweet(district, party, max_c, polarity);
        if (tweet == null) {
            // this can happen in the avg_sentiment case when the state has no data
            // on the winning class and it was only chosen as winning because
            // the other group had negative avg_sentiment
            tweet = this.get_tweet(district, party, max_c, 'combined');
        }
        return {
            'larger_group': max_c,
            'smaller_group': 'Other', // if only two given, we could specify the other candidate
            'larger_group_metric': larger_group_metric,
            'smaller_group_metric': smaller_group_metric,
            'tweet_text': tweet['tweet_text'],
            'username': tweet['username'],
            'likes': tweet['likes'],
            'sentiment': tweet['sentiment'],
            'tweet_date':  tweet['tweet_date'],
            'date_descriptor': tweet['date_descriptor'],
        };
    }

    get_hover_text_info_cp(district, democrats, republicans, metric, polarity) {
        let dem_total = 0;
        let rep_total = 0;
        let dem_c = null;
        let rep_c = null;
        if (metric === 'avg_sentiment') {
            const dem_res = this.get_average_sentiment_data(district, 'Democrat', democrats, polarity);
            dem_total = dem_res['avg_sentiment'];
            dem_c = dem_res['max_candidate'];
            const rep_res = this.get_average_sentiment_data(district, 'Republican', republicans, polarity);
            rep_total = rep_res['avg_sentiment'];
        }
        else {
            const dem_values = this.get_values(district, 'Democrat', democrats, metric, polarity);
            const rep_values = this.get_values(district, 'Republican', republicans, metric, polarity);
            let dem_contrib_m = 0;
            let rep_contrib_m = 0;
            if (dem_values === null) {
                dem_total = null;
            }
            else {
                for (let k in dem_values) {
                    dem_total += dem_values[k];
                    if (dem_values[k] > dem_contrib_m) {
                        dem_c = k;
                        dem_contrib_m = dem_values[k];
                    }
                }
            }
            if (rep_values === null) {
                rep_total = null;
            }
            else {
                for (let k in rep_values) {
                    rep_total += rep_values[k];
                    if (rep_values[k] > rep_contrib_m) {
                        rep_c = k;
                        rep_contrib_m = rep_values[k];
                    }
                }
            }
        }
        if (dem_total === null && rep_total === null) {
            return null;
        }
        if (dem_total === null) {
            dem_total = 0;
        }
        if (rep_total === null) {
            rep_total = 0;
        }
        let larger_group = 'Democrat';
        let smaller_group = 'Republican'
        let larger_group_metric = dem_total;
        let smaller_group_metric = rep_total;
        let max_c = dem_c;
        let smaller_max_c = rep_c;
        if (dem_total < rep_total) {
            // look for positive tweets
            larger_group = 'Republican';
            smaller_group = 'Democrat';
            larger_group_metric = rep_total;
            smaller_group_metric = dem_total;
            max_c = rep_c;
            smaller_max_c = dem_c;
        }
        if (polarity === 'combined') {
            // this tells the get_tweet function to get the largest contributor
            // but only using the most positive contributor
            polarity = 'P';
        }
        let tweet = this.get_tweet(district, larger_group, max_c, polarity);
        if (tweet == null) {
            // this can happen in the avg_sentiment case when the state has no data
            // on the winning class and it was only chosen as winning because
            // the other group had negative avg_sentiment
            tweet = this.get_tweet(district, smaller_group, smaller_max_c, polarity);
            if (tweet == null) {
                // if tweet is still null, try the most negative of the larger class
                tweet = this.get_tweet(district, larger_group, max_c, 'N');
                if (tweet == null) {
                    // if tweet is still null, try the most negative of the smaller class
                    tweet = this.get_tweet(district, smaller_group, smaller_max_c, 'N');
                }
            }
        }
        return {
            'larger_group': larger_group,
            'smaller_group': smaller_group,
            'larger_group_metric': larger_group_metric,
            'smaller_group_metric': smaller_group_metric,
            'tweet_text': tweet['tweet_text'],
            'username': tweet['username'],
            'likes': tweet['likes'],
            'sentiment': tweet['sentiment'],
            'tweet_date':  tweet['tweet_date'],
            'date_descriptor': tweet['date_descriptor'],
        };
    }

    get_hover_text_info(district, democrats, republicans, metric, polarity) {
        /** 
         * Returs dict with the following keys:
         * larger_group
         * smaller_group
         * larger_group_metric
         * smaller_group_metric
         * tweet_text
         * username
         * likes
         * sentiment
         * tweet_date
         * date_descriptor
        */
        if (democrats.length === 0 && republicans.length !== 0) {
            return this.get_hover_text_info_sp(district, 'Republican', republicans, metric, polarity);
        }
        else if (democrats.length !== 0 && republicans.length === 0) {
            return this.get_hover_text_info_sp(district, 'Democrat', democrats, metric, polarity);
        }
        else {
            return this.get_hover_text_info_cp(district, democrats, republicans, metric, polarity);
        }
    }
  }


