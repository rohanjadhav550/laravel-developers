<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Conversation;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ConversationController extends Controller
{
    /**
     * Store or update a conversation.
     * This is called by the idea-agent service after each message.
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'user_id' => ['required', 'integer', 'exists:users,id'],
            'thread_id' => ['required', 'string', 'max:255'],
            'title' => ['nullable', 'string', 'max:255'],
            'project_id' => ['nullable', 'integer', 'exists:projects,id'],
            'message_count' => ['nullable', 'integer'],
            'last_message' => ['nullable', 'string'],
        ]);

        $conversation = Conversation::updateOrCreate(
            ['thread_id' => $validated['thread_id']],
            [
                'user_id' => $validated['user_id'],
                'title' => $validated['title'] ?? 'New Conversation',
                'project_id' => $validated['project_id'] ?? null,
                'message_count' => $validated['message_count'] ?? 1,
                'last_message_at' => now(),
            ]
        );

        return response()->json([
            'success' => true,
            'data' => $conversation,
        ]);
    }

    /**
     * Get all conversations for a user.
     */
    public function index(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'user_id' => ['required', 'integer', 'exists:users,id'],
            'status' => ['nullable', 'string', 'in:active,archived,deleted'],
        ]);

        $conversations = Conversation::where('user_id', $validated['user_id'])
            ->when($validated['status'] ?? null, function ($query, $status) {
                return $query->where('status', $status);
            })
            ->orderBy('last_message_at', 'desc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $conversations,
        ]);
    }

    /**
     * Get a specific conversation by thread_id.
     */
    public function show(string $threadId): JsonResponse
    {
        $conversation = Conversation::where('thread_id', $threadId)->first();

        if (!$conversation) {
            return response()->json([
                'success' => false,
                'message' => 'Conversation not found.',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $conversation,
        ]);
    }
}
