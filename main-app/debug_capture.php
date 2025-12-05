<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

try {
    $solution = \App\Models\Solution::find(11);
    if (!$solution) {
        throw new Exception("Solution 11 not found");
    }
    echo "Dispatching job for solution {$solution->id}...\n";
    
    // We instantiate the job directly and call handle to debug immediately
    $job = new \App\Jobs\CaptureLearnedKnowledge($solution);
    $job->handle();
    
    echo "Job completed successfully!\n";
} catch (\Exception $e) {
    echo "Job failed: " . $e->getMessage() . "\n";
    echo $e->getTraceAsString();
}
