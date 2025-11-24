<?php

namespace App\Http\Controllers;

use App\Models\Project;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Inertia\Inertia;
use Inertia\Response;

class ProjectController extends Controller
{
    /**
     * Display a listing of the user's projects.
     */
    public function index(Request $request): Response
    {
        $projects = $request->user()
            ->projects()
            ->withCount('users')
            ->orderBy('name')
            ->get();

        return Inertia::render('projects/index', [
            'projects' => $projects,
        ]);
    }

    /**
     * Show the form for creating a new project.
     */
    public function create(): Response
    {
        return Inertia::render('projects/create');
    }

    /**
     * Store a newly created project in storage.
     */
    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'name' => ['required', 'string', 'max:255'],
            'slug' => [
                'required',
                'string',
                'max:255',
                'alpha_dash',
                Rule::unique(Project::class),
            ],
        ]);

        $project = Project::create([
            'name' => $validated['name'],
            'slug' => Str::lower($validated['slug']),
            'owner_id' => $request->user()->id,
        ]);

        $project->users()->attach($request->user()->id, ['role' => 'owner']);

        return redirect()->route('projects.home', $project)
            ->with('success', 'Project created successfully.');
    }

    /**
     * Switch to a different project.
     */
    public function switch(Request $request, Project $project): RedirectResponse
    {
        if (! $request->user()->projects()->where('projects.id', $project->id)->exists()) {
            abort(403, 'You do not have access to this project.');
        }

        session(['current_project_id' => $project->id]);

        return redirect()->route('projects.home', $project);
    }
}
