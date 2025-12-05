<?php

use App\Http\Controllers\ConversationController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\ProjectController;
use App\Http\Controllers\SolutionController;
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

    // Admin - Learned Knowledge
    Route::get('admin/learned-knowledge', [\App\Http\Controllers\LearnedKnowledgeController::class, 'index'])->name('admin.learned-knowledge.index');
    Route::post('admin/learned-knowledge/{id}/review', [\App\Http\Controllers\LearnedKnowledgeController::class, 'review'])->name('admin.learned-knowledge.review');

    // Admin - Knowledge Base Management
    Route::get('admin/knowledge-bases', [\App\Http\Controllers\KnowledgeBaseController::class, 'index'])->name('admin.knowledge.index');
    Route::get('admin/knowledge-bases/{id}', [\App\Http\Controllers\KnowledgeBaseController::class, 'show'])->name('admin.knowledge.show');
    Route::post('admin/knowledge-bases/{id}/upload', [\App\Http\Controllers\KnowledgeBaseController::class, 'upload'])->name('admin.knowledge.upload');
    Route::delete('admin/knowledge-bases/{id}/documents/{docId}', [\App\Http\Controllers\KnowledgeBaseController::class, 'destroyDocument'])->name('admin.knowledge.document.destroy');
    Route::post('admin/knowledge-bases/{id}/vectorize', [\App\Http\Controllers\KnowledgeBaseController::class, 'vectorize'])->name('admin.knowledge.vectorize');

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
            Route::get('chat', function (\App\Models\Project $project) {
                return Inertia::render('chat/index', [
                    'project' => $project,
                ]);
            })->name('projects.chat');

            Route::get('conversations', [ConversationController::class, 'index'])->name('projects.conversations');

            // Solutions
            Route::get('solutions', [SolutionController::class, 'index'])->name('projects.solutions');
            Route::get('solutions/{solution}', [SolutionController::class, 'show'])->name('solutions.show');
            Route::post('solutions/{solution}/approve-requirements', [SolutionController::class, 'approveRequirements'])->name('solutions.approve-requirements');
            Route::post('solutions/{solution}/approve-solution', [SolutionController::class, 'approveSolution'])->name('solutions.approve-solution');
            Route::post('solutions/{solution}/publish', [SolutionController::class, 'publish'])->name('solutions.publish');
            Route::post('solutions/{solution}/republish', [SolutionController::class, 'republish'])->name('solutions.republish');
            Route::post('solutions/{solution}/capture', [SolutionController::class, 'capture'])->name('solutions.capture'); // Manual capture
            Route::get('solutions/{solution}/progress', [SolutionController::class, 'progress'])->name('solutions.progress');


            // Chat file upload
            Route::post('chat/upload', [\App\Http\Controllers\ChatFileController::class, 'upload'])->name('chat.file.upload');
            Route::get('chat/files/{filename}', [\App\Http\Controllers\ChatFileController::class, 'download'])->name('chat.file.download');
            
            // Chat AI agent
            Route::post('chat/ask', [\App\Http\Controllers\ChatController::class, 'askAgent'])->name('chat.ask');
            Route::get('chat/history', [\App\Http\Controllers\ChatController::class, 'getHistory'])->name('chat.history');
        });
});

require __DIR__.'/settings.php';
