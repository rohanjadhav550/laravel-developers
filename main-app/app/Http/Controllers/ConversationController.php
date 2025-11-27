<?php

namespace App\Http\Controllers;

use App\Models\Conversation;
use App\Models\Project;
use Inertia\Inertia;
use Inertia\Response;

class ConversationController extends Controller
{
    /**
     * Display a listing of conversations for a project.
     */
    public function index(Project $project): Response
    {
        $conversations = Conversation::where('user_id', auth()->id())
            ->where('project_id', $project->id)
            ->where('status', 'active')
            ->orderBy('last_message_at', 'desc')
            ->get()
            ->map(function ($conversation) {
                return [
                    'id' => $conversation->id,
                    'thread_id' => $conversation->thread_id,
                    'title' => $conversation->title,
                    'message_count' => $conversation->message_count,
                    'last_message_at' => $conversation->last_message_at,
                    'created_at' => $conversation->created_at,
                ];
            });

        return Inertia::render('conversations/index', [
            'project' => $project,
            'conversations' => $conversations,
        ]);
    }
}
