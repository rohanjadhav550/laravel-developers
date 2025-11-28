<?php

use App\Http\Controllers\Api\AiSettingsApiController;
use App\Http\Controllers\Api\ConversationController;
use App\Http\Controllers\ChatFileController;
use Illuminate\Support\Facades\Route;

// Internal API for microservices (unauthenticated)
Route::get('internal/ai-settings', [AiSettingsApiController::class, 'getSettings']);
Route::post('internal/conversations', [ConversationController::class, 'store']);
Route::get('internal/conversations', [ConversationController::class, 'index']);
Route::get('internal/conversations/{threadId}', [ConversationController::class, 'show']);
Route::post('internal/conversations/requirements', [ConversationController::class, 'saveRequirements']);
Route::post('internal/conversations/solution', [ConversationController::class, 'saveSolution']);

Route::middleware(['auth', 'project'])->group(function () {
    Route::prefix('projects/{project}')->group(function () {
        // Chat file upload
        Route::post('chat/upload', [ChatFileController::class, 'upload'])->name('chat.file.upload');
        Route::get('chat/files/{filename}', [ChatFileController::class, 'download'])->name('chat.file.download');
    });
});
