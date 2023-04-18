<?php
$lines = array_filter(array_map(function ($line) {
    return strlen($line) ? explode(';', trim($line)) : null;
}, explode("\n", file_get_contents(__DIR__ . '/baseline.csv'))));

$lines = array_slice($lines, 1); // Remove header.

$problems_results = array_chunk($lines, 391, false);
foreach ($problems_results as $problem_results) {
    echo count($problem_results) . PHP_EOL;
    echo $problem_results[0][0] . PHP_EOL;
    $baseline = (float) $problem_results[0][6];
    echo 'No-FS: ' . $baseline . PHP_EOL;
    $results = array_chunk(array_slice($problem_results, 1), 10);
    foreach ($results as $config_results) {
        echo implode('|', [$config_results[0][3], $config_results[0][4], $config_results[0][5]]) . ': ';
        $sum = array_reduce($config_results, function ($prev, $row) { return $prev + (float) $row[6]; }, 0);
        $avg = $sum / count($config_results);
        echo $avg . ($baseline < $avg ? ' +' : '');
        echo PHP_EOL;
    }
}
