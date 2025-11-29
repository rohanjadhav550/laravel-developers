<?php

namespace App\Http\Controllers;

use App\Models\Project;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ChatController extends Controller
{
    /**
     * Send a question to the AI agent and get a response
     */
    public function askAgent(Request $request, Project $project)
    {
        $request->validate([
            'question' => 'required|string|max:5000',
            'thread_id' => 'nullable|string|max:255',
        ]);

        $question = $request->input('question');
        $threadId = $request->input('thread_id'); // For conversation continuity
        $agentUrl = env('IDEA_AGENT_URL', 'http://idea-agent:8000');

        // Get user's AI settings
        $aiSetting = auth()->user()->aiSetting;
        if (!$aiSetting) {
            return response()->json([
                'success' => false,
                'error' => 'Please configure your AI settings first at /settings/ai',
            ], 400);
        }

        try {
            $payload = [
                'question' => $question,
                'user_id' => auth()->id(),
                'project_id' => $project->id,
                // Pass AI settings directly to avoid circular requests
                'ai_provider' => $aiSetting->provider,
                'ai_api_key' => $aiSetting->api_key,
            ];

            // Include thread_id if provided for conversation continuity
            if ($threadId) {
                $payload['thread_id'] = $threadId;
            }

            Log::info('Sending request to AI Agent', [
                'question' => substr($question, 0, 100),
                'thread_id' => $threadId,
                'user_id' => auth()->id(),
            ]);

            $response = Http::timeout(300)->post("{$agentUrl}/ask", $payload);

            if ($response->successful()) {
                $data = $response->json();

                Log::info('AI Agent response received', [
                    'thread_id' => $data['thread_id'] ?? null,
                    'status' => $data['status'] ?? 'unknown',
                ]);

                return response()->json([
                    'success' => true,
                    'response' => $data['response'] ?? 'No response from agent',
                    'thread_id' => $data['thread_id'] ?? null,
                    'status' => $data['status'] ?? 'completed',
                ]);
            }

            // Handle configuration errors (400 status)
            if ($response->status() === 400) {
                $data = $response->json();
                $errorMessage = $data['detail'] ?? 'AI configuration error';

                Log::warning('AI Agent configuration error', [
                    'error' => $errorMessage,
                    'user_id' => auth()->id(),
                ]);

                return response()->json([
                    'success' => false,
                    'error' => $errorMessage,
                ], 400);
            }

            Log::error('AI Agent request failed', [
                'status' => $response->status(),
                'body' => $response->body(),
            ]);

            return response()->json([
                'success' => false,
                'error' => 'Failed to get response from AI agent',
            ], 500);

        } catch (\Exception $e) {
            Log::error('AI Agent connection error', [
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString(),
            ]);

            return response()->json([
                'success' => false,
                'error' => 'Could not connect to AI agent. Please try again later.',
                'details' => config('app.debug') ? $e->getMessage() : null,
            ], 500);
        }
    }

    /**
     * Get conversation history for a specific thread_id
     */
    public function getHistory(Request $request, Project $project)
    {
        $request->validate([
            'thread_id' => 'required|string|max:255',
        ]);

        $threadId = $request->input('thread_id');
        $agentUrl = env('IDEA_AGENT_URL', 'http://idea-agent:8000');

        try {
            $response = Http::timeout(10)->get("{$agentUrl}/conversation/{$threadId}");

            if ($response->successful()) {
                return response()->json([
                    'success' => true,
                    'data' => $response->json(),
                ]);
            }

            return response()->json([
                'success' => false,
                'error' => 'Failed to fetch conversation history',
            ], 500);

        } catch (\Exception $e) {
            Log::error('Error fetching conversation history', [
                'thread_id' => $threadId,
                'error' => $e->getMessage(),
            ]);

            return response()->json([
                'success' => false,
                'error' => 'Could not fetch conversation history',
            ], 500);
        }
    }
}
