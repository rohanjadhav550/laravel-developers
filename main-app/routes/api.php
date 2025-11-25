<?php

use App\Http\Controllers\ChatFileController;
use Illuminate\Support\Facades\Route;

Route::middleware(['auth', 'project'])->group(function () {
    Route::prefix('projects/{project}')->group(function () {
        // Chat file upload
        Route::post('chat/upload', [ChatFileController::class, 'upload'])->name('chat.file.upload');
        Route::get('chat/files/{filename}', [ChatFileController::class, 'download'])->name('chat.file.download');
    });
});
