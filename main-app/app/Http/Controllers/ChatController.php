<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class ChatController extends Controller
{
    /**
     * Send a question to the AI agent and get a response
     */
    public function askAgent(Request $request)
    {
        $request->validate([
            'question' => 'required|string|max:5000',
        ]);

        $question = $request->input('question');
        $agentUrl = env('IDEA_AGENT_URL', 'http://idea-agent:8000');

        try {
            $response = Http::timeout(30)->post("{$agentUrl}/ask", [
                'question' => $question,
            ]);

            if ($response->successful()) {
                $data = $response->json();
                return response()->json([
                    'success' => true,
                    'response' => $data['response'] ?? 'No response from agent',
                ]);
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
            ]);

            return response()->json([
                'success' => false,
                'error' => 'Could not connect to AI agent. Please try again later.',
            ], 500);
        }
    }
}
