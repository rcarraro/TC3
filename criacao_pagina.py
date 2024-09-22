import pandas as pd
import json
from datetime import datetime

current_date = datetime.now().strftime('%Y%m%d')
file_name = f'.\\historico_bitcoin\\bitcoin_data{current_date}.parquet'

df_features = pd.read_parquet(file_name)

df_features.reset_index(inplace=True)

df_features['timestamp'] = df_features['timestamp'].astype(str)

df_json = df_features[['timestamp', 'price', 'lag_1', 'lag_7', 'ma_7']].to_dict(orient='records')

with open("model_metrics.json", 'r') as f:
    model_metrics = json.load(f)

metrics_names = list(model_metrics[next(iter(model_metrics))].keys())
models = list(model_metrics.keys())
metrics_values = {metric: [model_metrics[model][metric] for model in models] for metric in metrics_names}

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" href="estilo.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>

<h1>Variação do Preço do Bitcoin</h1>
<div>
    <button class="button" onclick="updateGraph('price')">Preço</button>
    <button class="button" onclick="updateGraph('lag_1')">Lag 1 Dia</button>
    <button class="button" onclick="updateGraph('lag_7')">Lag 7 Dias</button>
    <button class="button" onclick="updateGraph('ma_7')">Média Móvel 7 Dias</button>
</div>
<div id="priceGraph"></div>

<h1>Métricas dos Modelos</h1>
<label for="metricSelect">Selecione a Métrica:</label>
<select id="metricSelect" onchange="updateMetricsGraph()">
    <option value="" disabled selected>Escolha uma métrica</option>
    {''.join(f'<option value="{metric}">{metric}</option>' for metric in metrics_names)}
</select>

<label for="modelSelect">Selecione o Modelo:</label>
<select id="modelSelect" onchange="updateMetricsGraph()">
    <option value="" disabled selected>Escolha um modelo</option>
    {''.join(f'<option value="{model}">{model}</option>' for model in models)}
</select>

<label for="showAllSelect">Mostrar:</label>
<select id="showAllSelect" size="3" onchange="updateMetricsGraph()">
    <option value="single">Métrica/Modelo Selecionado</option>
    <option value="all">Todas as Métricas para o Modelo</option>
    <option value="allModels">Todos os Modelos para a Métrica</option>
</select>

<div id="metricsGraph"></div>

<script>
    var data = {json.dumps(df_json, indent=4)};
    var metricsData = {json.dumps(metrics_values, indent=4)};
    var models = {json.dumps(models)};
    var metricsNames = {json.dumps(metrics_names)};

    let timestamps = data.map(d => d.timestamp);

    function updateGraph(variable) {{
        let values = data.map(d => d[variable]);
        
        var trace1 = {{
            x: timestamps,
            y: values,
            type: 'scatter',
            mode: 'lines',
            name: variable,
            line: {{ width: 2 }}
        }};

        var layout = {{
            title: 'Variação de ' + variable + ' do Bitcoin',
            xaxis: {{ title: 'Data' }},
            yaxis: {{ title: variable + ' (USD)' }},
            plot_bgcolor: '#f4f4f4',
            paper_bgcolor: '#f4f4f4'
        }};

        Plotly.newPlot('priceGraph', [trace1], layout);
    }}

    updateGraph('price');

    function updateMetricsGraph() {{
        var selectedMetric = document.getElementById('metricSelect').value;
        var selectedModel = document.getElementById('modelSelect').value;
        var showAll = document.getElementById('showAllSelect').value;

        var traces = [];

        if (showAll === 'single') {{
            var value = metricsData[selectedMetric][models.indexOf(selectedModel)];
            traces.push({{
                x: [selectedModel],
                y: [value],
                type: 'bar',
                name: selectedMetric,
                marker: {{ color: getColor(value, selectedMetric) }}
            }});
            var layout = {{
                title: 'Métrica ' + selectedMetric + ' para o modelo ' + selectedModel,
                xaxis: {{ title: 'Modelo' }},
                yaxis: {{ title: selectedMetric }},
                plot_bgcolor: '#f4f4f4',
                paper_bgcolor: '#f4f4f4'
            }};
        }} else if (showAll === 'all') {{
            for (var metric of metricsNames) {{
                var value = metricsData[metric][models.indexOf(selectedModel)];
                traces.push({{
                    x: [metric],
                    y: [value],
                    type: 'bar',
                    name: metric,
                    marker: {{ color: getColor(value, metric) }}
                }});
            }}
            var layout = {{
                title: 'Todas as Métricas para o modelo ' + selectedModel,
                xaxis: {{ title: 'Métricas' }},
                yaxis: {{ title: 'Valor', type: 'log' }}, // Escala logarítmica
                plot_bgcolor: '#f4f4f4',
                paper_bgcolor: '#f4f4f4',
                barmode: 'group'
            }};
        }} else if (showAll === 'allModels') {{
            for (var model of models) {{
                var value = metricsData[selectedMetric][models.indexOf(model)];
                traces.push({{
                    x: [model],
                    y: [value],
                    type: 'bar',
                    name: model,
                    marker: {{ color: getColor(value, selectedMetric) }}
                }});
            }}
            var layout = {{
                title: 'Todos os Modelos para a métrica ' + selectedMetric,
                xaxis: {{ title: 'Modelos' }},
                yaxis: {{ title: selectedMetric }},
                plot_bgcolor: '#f4f4f4',
                paper_bgcolor: '#f4f4f4'
            }};
        }}

        Plotly.newPlot('metricsGraph', traces, layout);
    }}

    updateMetricsGraph();
    
    function getColor(value, metric) {{
    if (metric === 'R²') {{
        let normalizedValue = (value - 0) / (1 - 0); // Assuming R² is between 0 and 1
        let red = Math.floor(255 * (1 - normalizedValue)); // Closer to red if worse
        let green = Math.floor(255 * normalizedValue); // Closer to green if better

        // Limit color values
        red = Math.max(0, Math.min(255, red));
        green = Math.max(0, Math.min(255, green));

        return 'rgba(' + red + ', ' + green + ', 0, 0.7)'; // Gradient from red to green
    }} else {{
        let min = Math.min(...metricsData[metric]);
        let max = Math.max(...metricsData[metric]);

        if (min === max) {{
            return 'rgb(255, 255, 0)'; // Yellow if all values are the same
        }}

        let range = max - min;
        let normValue = (value - min) / range;

        let red = Math.floor(255 * normValue);
        let green = 255 - red;

        red = Math.max(0, Math.min(255, red));
        green = Math.max(0, Math.min(255, green));

        return 'rgb(' + red + ', ' + green + ', 0)'; // Gradient from red to green
    }}
}}
</script>
</body>
</html>
"""

with open('index.html', 'w') as f:
    f.write(html_content)
