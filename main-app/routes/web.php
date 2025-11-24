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
        });
});

require __DIR__.'/settings.php';
