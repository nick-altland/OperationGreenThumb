function get_moist_data(callback, since) {
    var data = {};
    if (since !== undefined) {
        data.since = since
    }
    $.ajax({
        url: "/moisture",
        type: "GET",
        data: data,
        dataType: "json",
        success: function(response) {
            if (callback !== undefined) {
                var moist_datas = [];
                for (var i in response) {
                    var moist_list = response[i];
                    var moist_data = {
                        id: moist_list[0],
                        timestamp: moist_list[1],
                        level: moist_list[2]
                    };
                    moist_datas.push(moist_data);
                }
                callback(moist_datas);
            }
        }
    });
}

var latest_timestamp = "0";

function get_new_moist_data(callback) {
    get_moist_data(function(moists) {
        if (moists.length > 0) {
            latest_timestamp = moists[moists.length - 1].timestamp;
            console.log(latest_timestamp);
        }
        callback(moists);
    }, latest_timestamp)
}

var moist_chart;

function create_moist_chart(ctx) {
    moist_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "Moisture",
                data: []
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        max: y_max,
                        min: y_min
                    }
                }],
                xAxes: [{
                    ticks: {
                        autoSkip: true,
                        maxTicksLimit: 20
                    }
                }]
            }
        }
    });
}

var y_min = 0;
var y_max = 1;

function add_moist_to_chart(moist_value, time_label) {
    if (moist_value > y_max - 10) {
        y_max = moist_value + 10;
        moist_chart.options.scales.yAxes[0].ticks.max = y_max;
    }

    moist_chart.data.datasets[0].data.push(moist_value);
    moist_chart.data.labels.push(time_label);
}

function update_moist_chart() {
    moist_chart.update();
}

function update() {
    get_new_moist_data(function(moists) {
        for (var i in moists) {
            var moist = moists[i];

            $("<tr>" +
                "<td>" + moist.id + "</td>" +
                "<td>" + moist.timestamp + "</td>" +
                "<td>" + moist.level.toFixed(3) + "</td>" +
            "</tr>").prependTo($("#moist_tbody"));

            var date = new Date(moist.timestamp);
            var time_label = date.getMonth() + 1 + "/" + date.getDate() + " " + date.getHours() + ":" + date.getMinutes();

            add_moist_to_chart(moist.level, time_label);
        }
        if (moists.length > 0) {
            update_moist_chart();
        }
    });
}

$(document).ready(function() {
    var ctx = document.getElementById("moist_chart").getContext('2d');
    create_moist_chart(ctx);

    update();
    setInterval(update, 1000);
});
