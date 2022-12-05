
function get_temp_data(callback, since) {
    var data = {};
    if (since !== undefined) {
        data.since = since
    }
    $.ajax({
        url: "/temp",
        type: "GET",
        data: data,
        dataType: "json",
        success: function(response) {
            if (callback !== undefined) {
                var temp_datas = [];
                for (var i in response) {
                    var temp_list = response[i];
                    var temp_data = {
                        id: temp_list[0],
                        timestamp: temp_list[1],
                        value_c: temp_list[2],
                        value_f: temp_list[3]
                    };
                    temp_datas.push(temp_data);
                }
                callback(temp_datas);
            }
        }
    });
}

var latest_timestamp = "0";

function get_new_temp_data(callback) {
    get_temp_data(function(temps) {
        if (temps.length > 0) {
            latest_timestamp = temps[temps.length - 1].timestamp;
            console.log(latest_timestamp);
        }
        callback(temps);
    }, latest_timestamp)
}

var temp_chart;

function create_temp_chart(ctx) {
    temp_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: "Temperature",
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

function add_temp_to_chart(temp_value, time_label) {
    if (temp_value > y_max - 10) {
        y_max = temp_value + 10;
        temp_chart.options.scales.yAxes[0].ticks.max = y_max;
    }

    temp_chart.data.datasets[0].data.push(temp_value);
    temp_chart.data.labels.push(time_label);
}

function update_temp_chart() {
    temp_chart.update();
}

function update() {
    get_new_temp_data(function(temps) {
        for (var i in temps) {
            var temp = temps[i];

            $("<tr>" +
                "<td>" + temp.id + "</td>" +
                "<td>" + temp.timestamp + "</td>" +
                "<td>" + temp.value_f.toFixed(3) + "</td>" +
                "<td>" + temp.value_c.toFixed(3) + "</td>" +
            "</tr>").prependTo($("#temp_tbody"));

            var date = new Date(temp.timestamp);
            var time_label = date.getMonth() + 1 + "/" + date.getDate() + " " + date.getHours() + ":" + date.getMinutes();

            add_temp_to_chart(temp.value_f, time_label);
        }
        if (temps.length > 0) {
            update_temp_chart();
        }
    });
}

$(document).ready(function() {
    var ctx = document.getElementById("temp_chart").getContext('2d');
    create_temp_chart(ctx);

    update();
    setInterval(update, 1000);
});
