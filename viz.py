import logging
import json
import plotly
import plotly.graph_objects as go
import networkx as nx
from pwnagotchi import plugins
from flask import render_template_string, abort, jsonify
from threading import Lock

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
                ret = data;
            }
        });
        return ret;
        };

        function loadGraphData() {
            var data = ajaxDataRenderer('/plugins/viz/update');
            Plotly.newPlot('plot', data);
        }
        loadGraphData();
        setInterval(loadGraphData, 5000);
    });
{% endblock %}

{% block content %}
    <div class="chart" id="plot">
    </div>
{% endblock %}
"""

class Viz(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = "0.1.0"
    __license__ = "GPL3"
    __description__ = ""
    __dependencies__ = ['plotly', 'pandas', 'flask', 'networkx']

    def __init__(self):
        self.options = dict()
        self.data = None
        self.lock = Lock()

    def on_loaded(self):
        logging.info("Viz is loaded!")

    @staticmethod
    def create_graph(data):
        if not data:
            return {}
        # create networkx graph
        graph = nx.Graph()
        for ap_data in data:
            name = ap_data['hostname'] or ap_data['mac']
            graph.add_node(name, size = len(ap_data['clients']))

            for c in ap_data['clients']:
                cname = c['hostname'] or c['mac']
                graph.add_node(cname)
                graph.add_edge(name, cname)

        pos = nx.spring_layout(graph)
        for n, p in pos.items():
            graph.node[n]['pos'] = p

        # convert edges
        edge_x = list()
        edge_y = list()
        for edge in graph.edges():
            x0, y0 = graph.nodes[edge[0]]['pos']
            x1, y1 = graph.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        # convert nodes
        node_x = list()
        node_y = list()
        for node in graph.nodes():
            x, y = graph.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2))

        # Customize layout
        layout = go.Layout(
            paper_bgcolor='rgba(0,0,0,0)',  # transparent background
            plot_bgcolor='rgba(0,0,0,0)',  # transparent 2nd background
            xaxis =  {'showgrid': False, 'zeroline': False},  # no gridlines
            yaxis = {'showgrid': False, 'zeroline': False},  # no gridlines
        )

        # Create figure
        fig = go.Figure(layout = layout)

        # Add all edge traces
        for trace in edge_trace:
            fig.add_trace(trace)

        # Add node trace
        fig.add_trace(node_trace)

        # Remove legend
        fig.update_layout(showlegend = False)

        # Remove tick labels
        fig.update_xaxes(showticklabels = False)
        fig.update_yaxes(showticklabels = False)

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


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
