<?php

use App\Http\Controllers\Api\AiSettingsApiController;
use App\Http\Controllers\Api\ConversationController;
use App\Http\Controllers\Api\SolutionController;
use App\Http\Controllers\ChatFileController;
use Illuminate\Support\Facades\Route;

// Internal API for microservices (unauthenticated)
Route::get('internal/ai-settings', [AiSettingsApiController::class, 'getSettings']);
Route::post('internal/conversations', [ConversationController::class, 'store']);
Route::get('internal/conversations', [ConversationController::class, 'index']);
Route::get('internal/conversations/{threadId}', [ConversationController::class, 'show']);
Route::post('internal/conversations/requirements', [ConversationController::class, 'saveRequirements']);
Route::post('internal/conversations/solution', [ConversationController::class, 'saveSolution']);

// Solution management endpoints
Route::get('internal/solutions', [SolutionController::class, 'index']);
Route::get('internal/solutions/{id}', [SolutionController::class, 'show']);
Route::get('internal/solutions/conversation/{conversationId}', [SolutionController::class, 'getByConversation']);
Route::post('internal/solutions', [SolutionController::class, 'store']);
Route::put('internal/solutions/by-conversation', [SolutionController::class, 'updateRequirements']);
Route::put('internal/solutions/by-conversation/technical', [SolutionController::class, 'updateTechnicalSolution']);
Route::post('internal/solutions/{id}/approve-requirements', [SolutionController::class, 'approveRequirements']);
Route::post('internal/solutions/{id}/approve-solution', [SolutionController::class, 'approveSolution']);
Route::put('internal/solutions/{id}/status', [SolutionController::class, 'updateStatus']);
Route::delete('internal/solutions/{id}', [SolutionController::class, 'destroy']);

Route::middleware(['auth', 'project'])->group(function () {
    Route::prefix('projects/{project}')->group(function () {
        // Chat file upload
        Route::post('chat/upload', [ChatFileController::class, 'upload'])->name('chat.file.upload');
        Route::get('chat/files/{filename}', [ChatFileController::class, 'download'])->name('chat.file.download');
    });
});
