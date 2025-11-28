<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Solution;
use App\Models\Conversation;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class SolutionController extends Controller
{
    /**
     * Get all solutions for a user.
     */
    public function index(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'user_id' => ['required', 'integer', 'exists:users,id'],
            'status' => ['nullable', 'string', 'in:draft,in_progress,requirement_ready,solution_ready,approved,rejected,completed'],
        ]);

        $solutions = Solution::where('user_id', $validated['user_id'])
            ->when($validated['status'] ?? null, function ($query, $status) {
                return $query->where('status', $status);
            })
            ->with(['conversation', 'project'])
            ->orderBy('updated_at', 'desc')
            ->get();

        return response()->json([
            'success' => true,
            'data' => $solutions,
        ]);
    }

    /**
     * Get a specific solution by ID.
     */
    public function show(int $id): JsonResponse
    {
        $solution = Solution::with(['conversation', 'project', 'user'])->find($id);

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found.',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $solution,
        ]);
    }

    /**
     * Create a new solution for a conversation.
     * Called by the agent when a conversation starts.
     */
    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'conversation_id' => ['required', 'integer', 'exists:conversations,id'],
            'user_id' => ['required', 'integer', 'exists:users,id'],
            'project_id' => ['nullable', 'integer', 'exists:projects,id'],
            'title' => ['required', 'string', 'max:255'],
            'description' => ['nullable', 'string'],
            'status' => ['nullable', 'string', 'in:draft,in_progress,requirement_ready,solution_ready,approved,rejected,completed'],
        ]);

        // Check if solution already exists for this conversation
        $existingSolution = Solution::where('conversation_id', $validated['conversation_id'])->first();
        if ($existingSolution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution already exists for this conversation.',
                'data' => $existingSolution,
            ], 409);
        }

        $solution = Solution::create([
            'conversation_id' => $validated['conversation_id'],
            'user_id' => $validated['user_id'],
            'project_id' => $validated['project_id'] ?? null,
            'title' => $validated['title'],
            'description' => $validated['description'] ?? null,
            'status' => $validated['status'] ?? 'in_progress',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Solution created successfully.',
            'data' => $solution,
        ], 201);
    }

    /**
     * Update solution requirements.
     * Called by the requirement agent during conversation.
     */
    public function updateRequirements(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'conversation_id' => ['required', 'integer', 'exists:conversations,id'],
            'requirements' => ['required', 'string'],
        ]);

        $solution = Solution::where('conversation_id', $validated['conversation_id'])->first();

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found for this conversation.',
            ], 404);
        }

        $solution->update([
            'requirements' => $validated['requirements'],
            'status' => 'requirement_ready',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Requirements updated successfully.',
            'data' => $solution,
        ]);
    }

    /**
     * Update solution technical solution.
     * Called by the developer agent during conversation.
     */
    public function updateTechnicalSolution(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'conversation_id' => ['required', 'integer', 'exists:conversations,id'],
            'technical_solution' => ['required', 'string'],
        ]);

        $solution = Solution::where('conversation_id', $validated['conversation_id'])->first();

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found for this conversation.',
            ], 404);
        }

        $solution->update([
            'technical_solution' => $validated['technical_solution'],
            'status' => 'solution_ready',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Technical solution updated successfully.',
            'data' => $solution,
        ]);
    }

    /**
     * Approve requirements.
     * Called when user approves the gathered requirements.
     */
    public function approveRequirements(Request $request, int $id): JsonResponse
    {
        $solution = Solution::find($id);

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found.',
            ], 404);
        }

        $solution->update([
            'requirement_approved_at' => now(),
            'status' => 'approved',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Requirements approved successfully.',
            'data' => $solution,
        ]);
    }

    /**
     * Approve technical solution.
     * Called when user approves the proposed solution.
     */
    public function approveSolution(Request $request, int $id): JsonResponse
    {
        $solution = Solution::find($id);

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found.',
            ], 404);
        }

        $solution->update([
            'solution_approved_at' => now(),
            'status' => 'completed',
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Solution approved successfully.',
            'data' => $solution,
        ]);
    }

    /**
     * Update solution status.
     */
    public function updateStatus(Request $request, int $id): JsonResponse
    {
        $validated = $request->validate([
            'status' => ['required', 'string', 'in:draft,in_progress,requirement_ready,solution_ready,approved,rejected,completed'],
        ]);

        $solution = Solution::find($id);

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found.',
            ], 404);
        }

        $solution->update([
            'status' => $validated['status'],
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Status updated successfully.',
            'data' => $solution,
        ]);
    }

    /**
     * Delete a solution.
     */
    public function destroy(int $id): JsonResponse
    {
        $solution = Solution::find($id);

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found.',
            ], 404);
        }

        $solution->delete();

        return response()->json([
            'success' => true,
            'message' => 'Solution deleted successfully.',
        ]);
    }

    /**
     * Get solution by conversation ID.
     */
    public function getByConversation(int $conversationId): JsonResponse
    {
        $solution = Solution::where('conversation_id', $conversationId)
            ->with(['conversation', 'project', 'user'])
            ->first();

        if (!$solution) {
            return response()->json([
                'success' => false,
                'message' => 'Solution not found for this conversation.',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => $solution,
        ]);
    }
}
