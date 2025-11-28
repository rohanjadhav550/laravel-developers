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

        return redirect()->back()->with('success', 'Solution approved successfully.');
    }
}
