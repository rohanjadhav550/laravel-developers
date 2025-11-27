<?php

use App\Http\Controllers\HomeController;
use App\Http\Controllers\ProjectController;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use Laravel\Fortify\Features;

Route::get('/', function () {
    return Inertia::render('welcome', [
        'canRegister' => Features::enabled(Features::registration()),
    ]);
})->name('home');

Route::middleware(['auth'])->group(function () {
    // Projects management
    Route::get('projects', [ProjectController::class, 'index'])->name('projects.index');
    Route::get('projects/create', [ProjectController::class, 'create'])->name('projects.create');
    Route::post('projects', [ProjectController::class, 'store'])->name('projects.store');

    // Project-scoped routes
    Route::prefix('projects/{project}')
        ->middleware(['project'])
        ->group(function () {
            Route::get('home', HomeController::class)->name('projects.home');
            Route::post('switch', [ProjectController::class, 'switch'])->name('projects.switch');

            Route::get('dashboard', function () {
                return Inertia::render('dashboard');
            })->name('projects.dashboard');

            // Chat and AI features
            Route::get('chat', function () {
                $project = request()->route('project');
                return Inertia::render('chat/index', [
                    'project' => $project,
                ]);
            })->name('projects.chat');

            Route::get('conversations', function () {
                $project = request()->route('project');
                return Inertia::render('conversations/index', [
                    'project' => $project,
                ]);
            })->name('projects.conversations');

            Route::get('solutions', function () {
                $project = request()->route('project');
                return Inertia::render('solutions/index', [
                    'project' => $project,
                ]);
            })->name('projects.solutions');

            // Chat file upload
            Route::post('chat/upload', [\App\Http\Controllers\ChatFileController::class, 'upload'])->name('chat.file.upload');
            Route::get('chat/files/{filename}', [\App\Http\Controllers\ChatFileController::class, 'download'])->name('chat.file.download');
            
            // Chat AI agent
            Route::post('chat/ask', [\App\Http\Controllers\ChatController::class, 'askAgent'])->name('chat.ask');
        });
});

require __DIR__.'/settings.php';
