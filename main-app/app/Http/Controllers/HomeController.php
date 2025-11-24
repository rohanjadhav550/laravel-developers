<?php

namespace App\Http\Controllers;

use App\Models\Project;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Inertia\Response;

class HomeController extends Controller
{
    /**
     * Display the project home/dashboard.
     */
    public function __invoke(Request $request, Project $project): Response
    {
        return Inertia::render('home', [
            'project' => $project->load('owner'),
            'membersCount' => $project->users()->count(),
        ]);
    }
}
