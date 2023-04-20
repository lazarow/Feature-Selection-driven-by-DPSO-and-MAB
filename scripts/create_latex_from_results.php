<?php
$results = [
    'no-fs' => [],
    'grid-search' => [],
    'best-grid-search' => [],
    'best-grid-search-full' => [],
    'mab' => []
];

function sd_square($x, $mean) {
    return pow($x - $mean,2);
} 
function sd($array) {
    return sqrt(array_sum(array_map('sd_square', $array, array_fill(0,count($array), (array_sum($array) / count($array))))) / (count($array)-1));
}
function get_mean_and_sd($array) {
    $mean = array_sum($array) / count($array);
    $sd = sd($array);
    return [$mean, $sd];
}

#region No feature selection and the Grid Search.
$lines = array_filter(array_map(function ($line) {
    return strlen($line) ? explode(';', trim($line)) : null;
}, explode("\n", file_get_contents(__DIR__ . '/../no_fs-and-grid_search.csv'))));
$lines = array_slice($lines, 1); // Remove header.
$problems_results = array_chunk($lines, 251, false);
foreach ($problems_results as $problem_results) {
    $baseline = $problem_results[0];
    $results['no-fs'][$baseline[0]] = [
        'cost' => (float) $baseline[6],
        'accuracy' => (float) $baseline[7],
        'nof.features' => (int) $baseline[8],
        'time' => (float) $baseline[9],
    ];
    $results['grid-search'][$baseline[0]] = [];
    $results['best-grid-search'][$baseline[0]] = null;
    $grid_search_results = array_chunk(array_slice($problem_results, 1), 10);
    foreach ($grid_search_results as $config_results) {
        $metrics = [
            'c1' => (float) $config_results[0][3],
            'c2' => (float) $config_results[0][4],
            'cost' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($config_results, 6))),
            'accuracy' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($config_results, 7))),
            'nof.features' => get_mean_and_sd(array_map(function ($x) { return (int) $x; }, array_column($config_results, 8))),
            'time' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($config_results, 9))),
        ];
        $results['grid-search'][$baseline[0]][] = $metrics;
        if (
            is_null($results['best-grid-search'][$baseline[0]])
            || $metrics['cost'] < $results['best-grid-search'][$baseline[0]]['cost']
        ) {
            $results['best-grid-search'][$baseline[0]] = $metrics;
        }
    }
}
#endregion

#region MAB.
$lines = array_filter(array_map(function ($line) {
    return strlen($line) ? explode(';', trim($line)) : null;
}, explode("\n", file_get_contents(__DIR__ . '/../mab.csv'))));
$lines = array_slice($lines, 1); // Remove header.
$problems_results = array_chunk($lines, 40, false);
foreach ($problems_results as $problem_results) {
    $dataset = $problem_results[0][0];
    $results['mab'][$dataset] = [
        '25%' => [],
        '50%' => [],
        '75%' => [],
        '100%' => [],
    ];
    foreach ($problem_results as $run_results) {
        $results['mab'][$dataset][$run_results[4]][] = $run_results;
    }
    foreach ($results['mab'][$dataset] as $percent => $percent_result) {
        $results['mab'][$dataset][$percent] = [
            'nof.iteration' => (int) $percent_result[0][3],
            'cost' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($percent_result, 6))),
            'accuracy' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($percent_result, 7))),
            'nof.features' => get_mean_and_sd(array_map(function ($x) { return (int) $x; }, array_column($percent_result, 8))),
            'time' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($percent_result, 9))),
        ];
    }
}
#endregion

#region Best from Grid Search.
$lines = array_filter(array_map(function ($line) {
    return strlen($line) ? explode(';', trim($line)) : null;
}, explode("\n", file_get_contents(__DIR__ . '/../best_from_grid_search.csv'))));
$lines = array_slice($lines, 1); // Remove header.
$problems_results = array_chunk($lines, 40, false);
foreach ($problems_results as $problem_results) {
    $dataset = $problem_results[0][0];
    $results['best-grid-search-full'][$dataset] = [
        '25%' => [],
        '50%' => [],
        '75%' => [],
        '100%' => [],
    ];
    foreach ($problem_results as $run_results) {
        $results['best-grid-search-full'][$dataset][$run_results[4]][] = $run_results;
    }
    foreach ($results['best-grid-search-full'][$dataset] as $percent => $percent_result) {
        $results['best-grid-search-full'][$dataset][$percent] = [
            'nof.iteration' => (int) $percent_result[0][3],
            'cost' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($percent_result, 6))),
            'accuracy' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($percent_result, 7))),
            'nof.features' => get_mean_and_sd(array_map(function ($x) { return (int) $x; }, array_column($percent_result, 8))),
            'time' => get_mean_and_sd(array_map(function ($x) { return (float) $x; }, array_column($percent_result, 9))),
        ];
    }
}
#endregion

$datasets = [
    'soybean-large-preprocessed' => 'Soybean (Large) Data Set',
    'anneal-preprocessed' => 'Annealing Data Set',
    'arrhythmia-preprocessed' => 'Arrhythmia Data Set',
    'ad-preprocessed' => 'Internet Advertisements Data Set'
];

ob_start();
echo '\begin{figure}' . PHP_EOL;
$plot_configs = [
    'soybean-large-preprocessed' => ['legend at' => '0.98,0.98', 'legend anchor' => 'north east', 'ymax' => '0.3', 'ymin' => '0.08'],
    'anneal-preprocessed' => ['legend at' => '0.98,0.98', 'legend anchor' => 'north east', 'ymax' => '0.25', 'ymin' => '0.05'],
    'arrhythmia-preprocessed' => ['legend at' => '0.98,0.02', 'legend anchor' => 'south east', 'ymax' => '0.45', 'ymin' => '0.2'],
    'ad-preprocessed' => ['legend at' => '0.98,0.98', 'legend anchor' => 'north east', 'ymax' => '0.2', 'ymin' => '0.05'],
];
$first = true;
foreach ($results['grid-search'] as $dataset => $config_results) {
    if ($first) {
        $first = false;
    } else {
        echo '\hfill' . PHP_EOL;
        $first = true;
    }
    echo '  \begin{subfigure}{.49\textwidth}' . PHP_EOL;
    echo '      \centering' . PHP_EOL;
    echo '      \caption{' . $datasets[$dataset] . '}' . PHP_EOL;
    echo '      \begin{tikzpicture}[]' . PHP_EOL;
    echo '          \begin{axis}[ymin=' . $plot_configs[$dataset]['ymin'] . ',ymax=' . $plot_configs[$dataset]['ymax'] . ',compat=1.18,ylabel={Cost (the lower the better)},xlabel={An index of a configuration $m_i \in M$},symbolic x coords={' . implode(',', array_map(function ($i) {
        return '$' . ($i + 1) . '$';
    }, array_keys($config_results))) . '},legend style={at={(' . $plot_configs[$dataset]['legend at'] . ')},anchor=' . $plot_configs[$dataset]['legend anchor'] . ',font=\scriptsize},xtick=data,xticklabel style={font=\tiny},label style={font=\scriptsize},enlargelimits=0.02,ytick style={draw=none},xtick style={draw=none},yticklabel style={font=\scriptsize,/pgf/number format/fixed,/pgf/number format/precision=3},scaled y ticks=false]' . PHP_EOL;
    echo '              \addplot[mark=star,mark size=1][] coordinates {' . PHP_EOL;
    foreach (array_keys($config_results) as $i) {
        echo '                  ($' . ($i + 1) . '$, ' . round($results['no-fs'][$dataset]['cost'], 3) . ')' . PHP_EOL;
    }
    echo '              };' . PHP_EOL;
    echo '              \addlegendentry{No Feature Selection}' . PHP_EOL;
    echo '              \addplot[mark=square*,mark size=1][] coordinates {' . PHP_EOL;
    foreach ($config_results as $i => $metrics) {
        echo '                  ($' . ($i + 1) . '$, ' . round($metrics['cost'][0], 3) . ')' . PHP_EOL;
    }
    echo '              };' . PHP_EOL;
    echo '              \addlegendentry{Grid-Search}' . PHP_EOL;
    echo '              \addplot[mark=triangle*,mark size=1][] coordinates {' . PHP_EOL;
    foreach (array_keys($config_results) as $i) {
        echo '                  ($' . ($i + 1) . '$, ' . round($results['mab'][$dataset]['25%']['cost'][0], 3) . ')' . PHP_EOL;
    }
    echo '              };' . PHP_EOL;
    echo '              \addlegendentry{MAB (25\%)}' . PHP_EOL;
    echo '              \addplot[mark=diamond*,mark size=1][] coordinates {' . PHP_EOL;
    foreach (array_keys($config_results) as $i) {
        echo '                  ($' . ($i + 1) . '$, ' . round($results['mab'][$dataset]['100%']['cost'][0], 3) . ')' . PHP_EOL;
    }
    echo '              };' . PHP_EOL;
    echo '              \addlegendentry{MAB (100\%)}' . PHP_EOL;
    echo '          \end{axis}' . PHP_EOL;
    echo '      \end{tikzpicture}' . PHP_EOL;
    echo '  \end{subfigure}' . PHP_EOL;
}
echo '\caption{...}' . PHP_EOL;
echo '\label{fig:grid_search}' . PHP_EOL;
echo '\end{figure}' . PHP_EOL;
file_put_contents(__DIR__ . '/../Feature-Selection-driven-by-DPSO-and-MAB-Article/figure_grid_search.tex', ob_get_clean());

ob_start();
echo '\begin{table}[h]' . PHP_EOL;
echo '\caption{...}' . PHP_EOL;
echo '\label{tab:grid_search_vs_mab}' . PHP_EOL;
echo '\scriptsize' . PHP_EOL;
echo '\begin{tabular*}{\hsize}{@{\extracolsep{\fill}}llrrrrrr@{}}' . PHP_EOL;
echo '\toprule' . PHP_EOL;
echo 'Data Set';
echo ' & Metric';
echo ' & No-FS';
echo ' & DPSO\textsubscript{$m*$}';
echo ' & DPSO\textsubscript{MAB}';
echo ' & DPSO\textsubscript{MAB}';
echo ' & DPSO\textsubscript{MAB}';
echo ' & DPSO\textsubscript{MAB}';
echo '\\\\' . PHP_EOL;
echo '\colrule' . PHP_EOL;
echo ' & Nof. Iterations  & 1 & 100 & 620 (25\%) & 1250 (50\%) & 1880 (75\%) & 2500 (100\%)';
echo '\\\\' . PHP_EOL;
$table_metrics = [
    'cost' => 'Avg. Cost',
    'accuracy' => 'Avg. Accuracy',
    'nof.features' => 'Avg. Nof. Features',
    'time' => 'Avg. Time [s]'
];
foreach ($datasets as $dataset => $dataset_name) {
    $first = true;
    echo '\colrule' . PHP_EOL;
    foreach ($table_metrics as $metric => $metric_name) {
        if ($first) {
            echo '\multirow{' . count($table_metrics) . '}{*}{\parbox{2cm}{\raggedright ' . $dataset_name . '}}';
        }
        $precision = 3;
        if ($metric === 'nof.features') {
            $precision = 0;
        } else if ($metric === 'time') {
            $precision = 2;
        }
        echo ' & ' . $metric_name;
        echo ' & $' . number_format($results['no-fs'][$dataset][$metric], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['best-grid-search'][$dataset][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['best-grid-search'][$dataset][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['mab'][$dataset]['25%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['mab'][$dataset]['25%'][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['mab'][$dataset]['50%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['mab'][$dataset]['50%'][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['mab'][$dataset]['75%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['mab'][$dataset]['75%'][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['mab'][$dataset]['100%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['mab'][$dataset]['100%'][$metric][1], $precision, '.', '') . '$';
        echo '\\\\' . PHP_EOL;
        $first = false;
    }
}
echo '\botrule' . PHP_EOL;
echo '\end{tabular*}' . PHP_EOL;
echo '\end{table}' . PHP_EOL;
file_put_contents(__DIR__ . '/../Feature-Selection-driven-by-DPSO-and-MAB-Article/table_grid_search_vs_mab.tex', ob_get_clean());

ob_start();
echo '\begin{table}[h]' . PHP_EOL;
echo '\caption{...}' . PHP_EOL;
echo '\label{tab:grid_search_vs_mab}' . PHP_EOL;
echo '\scriptsize' . PHP_EOL;
echo '\begin{tabular*}{\hsize}{@{\extracolsep{\fill}}llrrrrr@{}}' . PHP_EOL;
echo '\toprule' . PHP_EOL;
echo 'Data Set';
echo ' & Metric';
echo ' & DPSO\textsubscript{$m*$}';
echo ' & DPSO\textsubscript{$m*$}';
echo ' & DPSO\textsubscript{$m*$}';
echo ' & DPSO\textsubscript{$m*$}';
echo ' & DPSO\textsubscript{MAB}';
echo '\\\\' . PHP_EOL;
echo '\colrule' . PHP_EOL;
echo ' & Nof. Iterations  & 620 (25\%) & 1250 (50\%) & 1880 (75\%) & 2500 (100\%) & 2500 (100\%)';
echo '\\\\' . PHP_EOL;
$table_metrics = [
    'cost' => 'Avg. Cost',
    'accuracy' => 'Avg. Accuracy',
    'nof.features' => 'Avg. Nof. Features',
    'time' => 'Avg. Time [s]'
];
foreach ($datasets as $dataset => $dataset_name) {
    $first = true;
    echo '\colrule' . PHP_EOL;
    foreach ($table_metrics as $metric => $metric_name) {
        if ($first) {
            echo '\multirow{' . count($table_metrics) . '}{*}{\parbox{2cm}{\raggedright ' . $dataset_name . '}}';
        }
        $precision = 3;
        if ($metric === 'nof.features') {
            $precision = 0;
        } else if ($metric === 'time') {
            $precision = 2;
        }
        echo ' & ' . $metric_name;
        echo ' & $' . number_format($results['best-grid-search-full'][$dataset]['25%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['best-grid-search-full'][$dataset]['25%'][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['best-grid-search-full'][$dataset]['50%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['best-grid-search-full'][$dataset]['50%'][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['best-grid-search-full'][$dataset]['75%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['best-grid-search-full'][$dataset]['75%'][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['best-grid-search-full'][$dataset]['100%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['best-grid-search-full'][$dataset]['100%'][$metric][1], $precision, '.', '') . '$';
        echo ' & $' . number_format($results['mab'][$dataset]['100%'][$metric][0], $precision, '.', '') . ' \pm ' . number_format($results['mab'][$dataset]['100%'][$metric][1], $precision, '.', '') . '$';
        echo '\\\\' . PHP_EOL;
        $first = false;
    }
}
echo '\botrule' . PHP_EOL;
echo '\end{tabular*}' . PHP_EOL;
echo '\end{table}' . PHP_EOL;
file_put_contents(__DIR__ . '/../Feature-Selection-driven-by-DPSO-and-MAB-Article/table_best_grid_search_vs_mab.tex', ob_get_clean());

function print_mean_and_sd($data) {
    return number_format($data[0], 4, '.', '') . ' ±' . number_format($data[1], 4, '.', '');
}
foreach(array_keys($datasets) as $dataset) {
    echo $datasets[$dataset] . ' (' . $dataset . '):' . PHP_EOL;
    echo '- No feature selection:' . PHP_EOL;
    echo '  - Cost: ' . $results['no-fs'][$dataset]['cost'] . PHP_EOL;
    echo '  - Accuracy: ' . $results['no-fs'][$dataset]['accuracy'] . PHP_EOL;
    echo '  - Nof. Features: ' . $results['no-fs'][$dataset]['nof.features'] . PHP_EOL;
    echo '- Best from Grid Search (c1=' . $results['best-grid-search'][$dataset]['c1'] . ', c2=' . $results['best-grid-search'][$dataset]['c2'] . '):' . PHP_EOL;
    echo '  - Cost: ' . print_mean_and_sd($results['best-grid-search'][$dataset]['cost']) . PHP_EOL;
    echo '  - Accuracy: ' . print_mean_and_sd($results['best-grid-search'][$dataset]['accuracy']) . PHP_EOL;
    echo '  - Nof. Features: ' . print_mean_and_sd($results['best-grid-search'][$dataset]['nof.features']) . PHP_EOL;
    foreach (['25%', '50%', '75%', '100%'] as $percent) {
        echo '- MAB (' . $percent . '):' . PHP_EOL;
        echo '  - Cost: ' . print_mean_and_sd($results['mab'][$dataset][$percent]['cost']) . PHP_EOL;
        echo '  - Accuracy: ' . print_mean_and_sd($results['mab'][$dataset][$percent]['accuracy']) . PHP_EOL;
        echo '  - Nof. Features: ' . print_mean_and_sd($results['mab'][$dataset][$percent]['nof.features']) . PHP_EOL;
    }
    foreach (['25%', '50%', '75%', '100%'] as $percent) {
        echo '- Best from Grid Search Full (' . $percent . '):' . PHP_EOL;
        echo '  - Cost: ' . print_mean_and_sd($results['best-grid-search-full'][$dataset][$percent]['cost']) . PHP_EOL;
        echo '  - Accuracy: ' . print_mean_and_sd($results['best-grid-search-full'][$dataset][$percent]['accuracy']) . PHP_EOL;
        echo '  - Nof. Features: ' . print_mean_and_sd($results['best-grid-search-full'][$dataset][$percent]['nof.features']) . PHP_EOL;
    }
}


