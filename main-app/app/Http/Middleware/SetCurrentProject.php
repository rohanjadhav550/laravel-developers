<?php

namespace App\Http\Middleware;

use App\Models\Project;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class SetCurrentProject
{
    /**
     * Handle an incoming request.
     */
    public function handle(Request $request, Closure $next): Response
    {
        $project = $request->route('project');

        if ($project instanceof Project) {
            if (! $request->user()->projects()->where('projects.id', $project->id)->exists()) {
                abort(403, 'You do not have access to this project.');
            }

            session(['current_project_id' => $project->id]);

            $request->attributes->set('current_project', $project);
        }

        return $next($request);
    }
}
