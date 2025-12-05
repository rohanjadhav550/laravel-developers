<?php

namespace App\Http\Controllers;

use App\Models\Solution;
use App\Models\Project;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class SolutionController extends Controller
{
    /**
     * Display a listing of solutions.
     */
    public function index(Project $project, Request $request): Response
    {
        $perPage = $request->integer('per_page', 10);
        $search = $request->string('search', '');
        $status = $request->string('status', '');

        $solutions = $request->user()
            ->solutions()
            ->with(['conversation', 'project'])
            ->when($search, function ($query, $search) {
                $query->where('title', 'like', "%{$search}%")
                    ->orWhere('description', 'like', "%{$search}%");
            })
            ->when($status, function ($query, $status) {
                $query->where('status', $status);
            })
            ->orderBy('updated_at', 'desc')
            ->paginate($perPage)
            ->withQueryString();

        return Inertia::render('solutions/index', [
            'project' => $project,
            'solutions' => $solutions,
            'filters' => [
                'search' => $search,
                'status' => $status,
                'per_page' => $perPage,
            ],
            'statuses' => [
                'draft' => 'Draft',
                'in_progress' => 'In Progress',
                'requirement_ready' => 'Requirement Ready',
                'solution_ready' => 'Solution Ready',
                'approved' => 'Approved',
                'rejected' => 'Rejected',
                'completed' => 'Completed',
            ],
        ]);
    }

    /**
     * Display the specified solution.
     */
    public function show(Project $project, Solution $solution): Response
    {
        // Ensure user owns this solution
        $this->authorize('view', $solution);

        $solution->load(['conversation', 'project', 'user']);

        return Inertia::render('solutions/show', [
            'project' => $project,
            'solution' => $solution,
        ]);
    }

    /**
     * Approve requirements for a solution.
     */
    public function approveRequirements(Project $project, Solution $solution)
    {
        $this->authorize('update', $solution);

        $solution->update([
            'requirement_approved_at' => now(),
            'status' => 'approved',
        ]);

        return redirect()->back()->with('success', 'Requirements approved successfully.');
    }

    /**
     * Approve solution.
     */
    public function approveSolution(Project $project, Solution $solution)
    {
        $this->authorize('update', $solution);

        $solution->update([
            'solution_approved_at' => now(),
            'status' => 'completed',
        ]);

        // Dispatch job to capture learned knowledge
        \App\Jobs\CaptureLearnedKnowledge::dispatch($solution);

        return redirect()->back()->with('success', 'Solution approved successfully.');
    }

    /**
     * Publish technical solution (trigger AI generation).
     */
    public function publish(Project $project, Solution $solution)
    {
        $this->authorize('update', $solution);

        // Validate that requirements exist
        if (empty($solution->requirements)) {
            return response()->json([
                'success' => false,
                'message' => 'Requirements must be completed before publishing solution.'
            ], 422);
        }

        // Check if already generating
        $progressKey = "solution_generation_{$solution->id}";
        $existingProgress = \Cache::get($progressKey);

        if ($existingProgress && in_array($existingProgress['status'], ['starting', 'analyzing', 'generating', 'saving'])) {
            return response()->json([
                'success' => false,
                'message' => 'Solution generation is already in progress.'
            ], 409);
        }

        // Dispatch job
        \App\Jobs\GenerateTechnicalSolution::dispatch($solution, false);

        return response()->json([
            'success' => true,
            'message' => 'Technical solution generation started. This may take 2-5 minutes.',
            'solution_id' => $solution->id
        ]);
    }

    /**
     * Republish technical solution (regenerate).
     */
    public function republish(Project $project, Solution $solution)
    {
        $this->authorize('update', $solution);

        // Validate that requirements exist
        if (empty($solution->requirements)) {
            return response()->json([
                'success' => false,
                'message' => 'Requirements must exist before republishing solution.'
            ], 422);
        }

        // Check if already generating
        $progressKey = "solution_generation_{$solution->id}";
        $existingProgress = \Cache::get($progressKey);

        if ($existingProgress && in_array($existingProgress['status'], ['starting', 'analyzing', 'generating', 'saving'])) {
            return response()->json([
                'success' => false,
                'message' => 'Solution generation is already in progress.'
            ], 409);
        }

        // Dispatch job
        \App\Jobs\GenerateTechnicalSolution::dispatch($solution, true);

        return response()->json([
            'success' => true,
            'message' => 'Technical solution regeneration started. This may take 2-5 minutes.',
            'solution_id' => $solution->id
        ]);
    }

    /**
     * Get solution generation progress.
     */
    public function progress(Project $project, Solution $solution)
    {
        $this->authorize('view', $solution);

        $progressKey = "solution_generation_{$solution->id}";
        $progress = \Cache::get($progressKey);

        if (!$progress) {
            return response()->json([
                'status' => 'idle',
                'progress' => 0,
                'message' => 'No generation in progress'
            ]);
        }

        return response()->json($progress);
    }

    /**
     * Manually capture learned knowledge from a solution.
     */
    public function capture(Project $project, Solution $solution, Request $request)
    {
        $this->authorize('update', $solution);
        
        $type = $request->input('type', 'all');

        if ($type === 'technical' && !$solution->technical_solution) {
            return redirect()->back()->with('error', 'Cannot capture technical knowledge: Solution is missing.');
        }
        
        if ($type === 'requirements' && !$solution->requirements) {
            return redirect()->back()->with('error', 'Cannot capture requirements: Requirements are missing.');
        }

        // Dispatch job to capture learned knowledge
        \App\Jobs\CaptureLearnedKnowledge::dispatch($solution, $type);

        $msg = match($type) {
            'requirements' => 'Requirements capture triggered successfully.',
            'technical' => 'Technical solution capture triggered successfully.',
            default => 'Learned knowledge capture triggered successfully.'
        };

        return redirect()->back()->with('success', $msg);
    }

}

