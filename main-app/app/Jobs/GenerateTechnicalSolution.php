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
use Illuminate\Support\Facades\Cache;

class GenerateTechnicalSolution implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * The number of seconds the job can run before timing out.
     */
    public $timeout = 600; // 10 minutes

    /**
     * The number of times the job may be attempted.
     */
    public $tries = 2;

    /**
     * Create a new job instance.
     */
    public function __construct(
        public Solution $solution,
        public bool $isRepublish = false
    ) {}

    /**
     * Execute the job.
     */
    public function handle(): void
    {
        try {
            // Update status to generating
            $this->solution->update([
                'status' => 'generating_solution'
            ]);

            // Set cache key for progress tracking
            $progressKey = "solution_generation_{$this->solution->id}";
            Cache::put($progressKey, [
                'status' => 'starting',
                'progress' => 0,
                'message' => 'Initializing deep-dive analysis...'
            ], 600);

            Log::info("Starting solution generation", [
                'solution_id' => $this->solution->id,
                'is_republish' => $this->isRepublish
            ]);

            // Update progress
            Cache::put($progressKey, [
                'status' => 'analyzing',
                'progress' => 25,
                'message' => 'Analyzing requirements with intelligent AI model...'
            ], 600);

            // Get user's AI configuration
            $user = $this->solution->user;
            $aiSettings = $user->aiSetting;

            if (!$aiSettings) {
                throw new \Exception('AI settings not configured. Please configure your AI settings.');
            }

            // Prepare request to idea-agent
            $endpoint = $this->isRepublish ? '/republish' : '/publish';
            $ideaAgentUrl = config('services.idea_agent.url', 'http://idea-agent:8001');

            Cache::put($progressKey, [
                'status' => 'generating',
                'progress' => 50,
                'message' => 'Generating comprehensive A-Z implementation guide (this may take 2-5 minutes)...'
            ], 600);

            // Call idea-agent service
            $response = Http::timeout(600) // 10 minutes timeout
                ->post("{$ideaAgentUrl}{$endpoint}", [
                    'thread_id' => $this->solution->conversation->thread_id,
                    'requirements' => $this->solution->requirements,
                    'user_id' => $user->id,
                    'ai_provider' => $aiSettings->provider,
                    'ai_api_key' => $aiSettings->api_key, // Already decrypted by Laravel's encrypted cast
                ]);

            if (!$response->successful()) {
                throw new \Exception("Idea agent returned error: " . $response->body());
            }

            Cache::put($progressKey, [
                'status' => 'saving',
                'progress' => 90,
                'message' => 'Saving technical solution...'
            ], 600);

            $data = $response->json();

            // Update solution with technical documentation
            $this->solution->update([
                'technical_solution' => $data['solution'],
                'status' => 'solution_ready',
                'generated_at' => now(),
                'metadata' => [
                    'model_used' => $data['metadata']['model_used'] ?? 'unknown',
                    'word_count' => $data['metadata']['word_count'] ?? 0,
                    'char_count' => $data['metadata']['char_count'] ?? 0,
                    'is_republish' => $this->isRepublish,
                ]
            ]);

            // Complete
            Cache::put($progressKey, [
                'status' => 'completed',
                'progress' => 100,
                'message' => 'Technical solution generated successfully!'
            ], 600);

            Log::info("Solution generation completed", [
                'solution_id' => $this->solution->id,
                'word_count' => $data['metadata']['word_count'] ?? 0
            ]);

        } catch (\Exception $e) {
            Log::error("Solution generation failed", [
                'solution_id' => $this->solution->id,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            // Update solution status to failed
            $this->solution->update([
                'status' => 'generation_failed'
            ]);

            // Update cache with error
            $progressKey = "solution_generation_{$this->solution->id}";
            Cache::put($progressKey, [
                'status' => 'failed',
                'progress' => 0,
                'message' => 'Failed to generate solution: ' . $e->getMessage()
            ], 600);

            throw $e;
        }
    }

    /**
     * Handle a job failure.
     */
    public function failed(\Throwable $exception): void
    {
        Log::error("Solution generation job failed permanently", [
            'solution_id' => $this->solution->id,
            'error' => $exception->getMessage()
        ]);

        $progressKey = "solution_generation_{$this->solution->id}";
        Cache::put($progressKey, [
            'status' => 'failed',
            'progress' => 0,
            'message' => 'Generation failed: ' . $exception->getMessage()
        ], 600);
    }
}
