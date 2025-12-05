<?php

namespace App\Jobs;

use App\Models\Solution;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class CaptureLearnedKnowledge implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * The number of seconds the job can run before timing out.
     */
    public $timeout = 60;

    /**
     * The number of times the job may be attempted.
     */
    public $tries = 3;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public Solution $solution,
        public string $captureType = 'all' // 'all', 'requirements', 'technical'
    ) {}

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        try {
            $kbAdminUrl = env('KB_ADMIN_URL', 'http://kb-admin:8000');
            $capturedIds = [];
            $shouldCaptureReq = $this->captureType === 'all' || $this->captureType === 'requirements';
            $shouldCaptureTech = $this->captureType === 'all' || $this->captureType === 'technical';

            // 1. Capture Requirements for Requirement Agent (Idea Agent)
            if ($shouldCaptureReq && $this->solution->requirements) {
                Log::info("Capturing requirements for Requirement Agent", ['solution_id' => $this->solution->id]);
                
                $reqPayload = [
                    'agent_type' => 'requirement_agent',
                    'knowledge_type' => 'solution_pattern',
                    'source_thread_id' => $this->solution->conversation->thread_id ?? 'manual',
                    'source_conversation_id' => $this->solution->conversation_id,
                    'question' => "Requirement Pattern: " . $this->solution->title,
                    'answer' => $this->solution->requirements,
                    'context' => [
                        'project_id' => $this->solution->project_id,
                        'source' => 'laravel_app_approval',
                        'type' => 'requirements'
                    ],
                    'confidence_score' => 1.0
                ];

                $response = Http::timeout(30)->post("{$kbAdminUrl}/api/learning/capture", $reqPayload);
                
                if ($response->successful()) {
                    $capturedIds['requirements'] = $response->json('id');
                } else {
                    Log::warning("Failed to capture requirements: " . $response->body());
                    if ($this->captureType === 'requirements') {
                         throw new \Exception("KB-Admin returned error: " . $response->body());
                    }
                }
            }

            // 2. Capture Technical Solution for Developer Agent
            if ($shouldCaptureTech && $this->solution->technical_solution) {
                Log::info("Capturing technical solution for Developer Agent", ['solution_id' => $this->solution->id]);

                $devPayload = [
                    'agent_type' => 'developer_agent',
                    'knowledge_type' => 'solution_pattern',
                    'source_thread_id' => $this->solution->conversation->thread_id ?? 'manual',
                    'source_conversation_id' => $this->solution->conversation_id,
                    'question' => "Technical Solution Pattern: " . $this->solution->title,
                    'answer' => $this->solution->technical_solution,
                    'context' => [
                        'project_id' => $this->solution->project_id,
                        'source' => 'laravel_app_approval',
                        'type' => 'technical_solution'
                    ],
                    'confidence_score' => 1.0
                ];

                $devResponse = Http::timeout(30)->post("{$kbAdminUrl}/api/learning/capture", $devPayload);

                if ($devResponse->successful()) {
                    $capturedIds['technical_solution'] = $devResponse->json('id');
                } else {
                    Log::warning("Failed to capture technical solution: " . $devResponse->body());
                    if ($this->captureType === 'technical' || (empty($capturedIds) && $this->captureType === 'all')) {
                        throw new \Exception("KB-Admin returned error: " . $devResponse->body());
                    }
                }
            }


            Log::info("Successfully captured learned knowledge", [
                'solution_id' => $this->solution->id,
                'captured_ids' => $capturedIds
            ]);

            // Update metadata to mark as captured
            $metadata = $this->solution->metadata ?? [];
            $metadata['learned_knowledge_captured_at'] = now()->toIso8601String();
            $metadata['learned_knowledge_ids'] = $capturedIds;
            
            $this->solution->update(['metadata' => $metadata]);

        } catch (\Exception $e) {
            Log::error("Failed to capture learned knowledge", [
                'solution_id' => $this->solution->id,
                'error' => $e->getMessage()
            ]);
            
            // We don't rethrow because this is a side-effect and shouldn't fail the main flow
            // But since it's a queued job, we could rethrow to retry. 
            // Given 'tries = 3', let's rethrow to allow retry.
            throw $e;
        }
    }
}
