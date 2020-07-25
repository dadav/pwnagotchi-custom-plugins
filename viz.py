import logging
import json
import plotly
import plotly.graph_objects as go
from random import random, choice
from math import pi, cos, sin
from plotly.validators.scatter.marker import SymbolValidator
from pwnagotchi import plugins
from flask import render_template_string, abort, jsonify
from threading import Lock
from pwnagotchi.mesh.wifi import freq_to_channel


TEMPLATE = """
{% extends "base.html" %}

{% set active_page = "plugins" %}

{% block title %}
    Viz
{% endblock %}

{% block scripts %}
    {{ super() }}
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
{% endblock %}

{% block script %}
    $(document).ready(function(){
        var ajaxDataRenderer = function(url, plot, options) {
        var ret = null;
        $.ajax({
            async: false,
            url: url,
            dataType:"json",
            success: function(data) {
                ret = JSON.parse(data);
            }
        });
        return ret;
        };

        function loadGraphData() {
            var layout = {
                title: 'Viz Map',
                showlegend: false,
                xaxis: {
                    title: {
                        text: 'Distance',
                    },
                },
                yaxis: {
                    title: {
                        text: 'Channel',
                    }
                }
            };
            var result = ajaxDataRenderer('/plugins/viz/update');
            if (Object.keys(result).length) == 0 {
                $('#plot').text('Waiting for data');
            } else {
                Plotly.newPlot('plot', result, layout);
            }
        }
        loadGraphData();
        setInterval(loadGraphData, 60000);
    });
{% endblock %}

{% block content %}
    <div class="chart" id="plot">
    </div>
{% endblock %}
"""

class Viz(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = "0.2.1"
    __license__ = "GPL3"
    __description__ = ""
    __dependencies__ = ['plotly', 'pandas', 'flask']

    COLORS = ['red', 'orange', 'yellow', 'lime green', 'green',
                    'blue-green', 'cyan', 'sky blue', 'blue', 'purple',
                    'magenta', 'pink']
    COLOR_MEMORY = dict()

    def __init__(self):
        self.options = dict()
        self.data = None
        self.lock = Lock()

    def on_loaded(self):
        logging.info("Viz is loaded!")

    @staticmethod
    def lookup_color(node):
        if node not in Viz.COLOR_MEMORY:
            Viz.COLOR_MEMORY[node] = choice(Viz.COLORS)
        return Viz.COLOR_MEMORY[node]

    @staticmethod
    def random_pos(x0 ,y0, r):
        w = r * random()
        t = 2 * pi * random()
        x = w * cos(t)
        y = w * sin(t)
        return x+x0, y+y0

    @staticmethod
    def create_graph(data):
        if not data:
            return {}

        node_text = list()
        edge_x = list()
        edge_y = list()
        node_x = list()
        node_y = list()
        node_symbols = list()
        node_sizes = list()
        node_colors = list()

        for ap_data in data:
            name = ap_data['hostname'] or ap_data['vendor'] or ap_data['mac']
            color = Viz.lookup_color(name)
            # nodes
            x, y = abs(ap_data['rssi']), freq_to_channel(ap_data['frequency'])
            node_x.append(x)
            node_y.append(y)
            node_text.append(name)
            node_symbols.append('square')
            node_sizes.append(10 + len(ap_data['clients']))
            node_colors.append(color)

            for c in ap_data['clients']:
                # node
                cname = c['hostname'] or c['vendor'] or c['mac']
                r = abs(x - abs(c['rssi']))
                xx, yy = Viz.random_pos(x,y,r)
                node_x.append(xx)
                node_y.append(yy)
                node_text.append(cname)
                node_symbols.append('circle')
                node_sizes.append(10)
                node_colors.append(color)

                # edge
                edge_x.append(x)
                edge_x.append(xx)
                edge_x.append(None)
                edge_y.append(y)
                edge_y.append(yy)
                edge_y.append(None)


        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker_symbol=node_symbols,
            marker_size=node_sizes,
            hovertext=node_text,
            hoverinfo='text')

        return json.dumps((edge_trace, node_trace), cls=plotly.utils.PlotlyJSONEncoder)


    def on_unfiltered_ap_list(self, agent, data):
        with self.lock:
            self.data = data

    def on_webhook(self, path, request):
        if not path or path == "/":
            return render_template_string(TEMPLATE)

        if path == 'update':
            with self.lock:
                g = Viz.create_graph(self.data)
                return jsonify(g)

        abort(404)
