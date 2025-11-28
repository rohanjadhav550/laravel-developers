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

    /**
     * Get conversations for a specific project and user.
     */
    public function getProjectConversations(Request $request, int $projectId): JsonResponse
    {
        $validated = $request->validate([
            'user_id' => ['required', 'integer', 'exists:users,id'],
        ]);

        $conversations = Conversation::where('user_id', $validated['user_id'])
            ->where('project_id', $projectId)
            ->where('status', 'active')
            ->orderBy('last_message_at', 'desc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $conversations,
        ]);
    }

    /**
     * Save requirements for a conversation.
     * Called by the requirement agent after gathering requirements.
     */
    public function saveRequirements(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'thread_id' => ['required', 'string', 'exists:conversations,thread_id'],
            'requirements' => ['required', 'string'],
        ]);

        $conversation = Conversation::where('thread_id', $validated['thread_id'])->first();

        if (!$conversation) {
            return response()->json([
                'success' => false,
                'message' => 'Conversation not found.',
            ], 404);
        }

        $conversation->update([
            'requirements' => $validated['requirements'],
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Requirements saved successfully.',
            'data' => $conversation,
        ]);
    }

    /**
     * Save solution for a conversation.
     * Called by the developer agent after proposing a solution.
     */
    public function saveSolution(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'thread_id' => ['required', 'string', 'exists:conversations,thread_id'],
            'solution' => ['required', 'string'],
        ]);

        $conversation = Conversation::where('thread_id', $validated['thread_id'])->first();

        if (!$conversation) {
            return response()->json([
                'success' => false,
                'message' => 'Conversation not found.',
            ], 404);
        }

        $conversation->update([
            'solution' => $validated['solution'],
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Solution saved successfully.',
            'data' => $conversation,
        ]);
    }
}
