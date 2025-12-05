<?php

namespace App\Console\Commands;

use App\Jobs\CaptureLearnedKnowledge;
use App\Models\Solution;
use Illuminate\Console\Command;

class BackfillLearnedKnowledge extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'kb:backfill-solutions';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Backfill learned knowledge from existing completed solutions';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $this->info("Starting backfill of learned knowledge...");

        // Debug: Count total completed solutions
        $totalCompleted = Solution::where('status', 'completed')->count();
        $this->info("Found {$totalCompleted} solutions with status 'completed'.");

        $solutions = Solution::where('status', 'completed')->get();

        $count = 0;
        $skipped = 0;

        foreach ($solutions as $solution) {
            $metadata = $solution->metadata ?? [];
            
            if (isset($metadata['learned_knowledge_captured_at'])) {
                $this->line("Skipping Solution ID {$solution->id}: Already captured.");
                $skipped++;
                continue;
            }

            $this->info("Dispatching capture job for Solution ID: {$solution->id}");
            try {
                CaptureLearnedKnowledge::dispatch($solution);
                $count++;
            } catch (\Exception $e) {
                $this->error("Failed to dispatch ID {$solution->id}: " . $e->getMessage());
            }
        }

        $this->info("Backfill complete! Dispatched: {$count} jobs. Skipped: {$skipped} already captured.");
    }
}
