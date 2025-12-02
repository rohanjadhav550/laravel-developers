<?php

use App\Models\Project;
use App\Models\Solution;
use App\Models\User;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Queue;

test('guests cannot publish solution', function () {
    $solution = Solution::factory()->requirementReady()->create();
    $project = $solution->project;

    $this->postJson("/projects/{$project->slug}/solutions/{$solution->id}/publish")
        ->assertUnauthorized();
});

test('users cannot publish solutions they do not own', function () {
    $owner = User::factory()->create();
    $otherUser = User::factory()->create();

    $solution = Solution::factory()
        ->requirementReady()
        ->for($owner, 'user')
        ->create();
    $project = $solution->project;

    // Attach project to owner but not otherUser
    $owner->projects()->attach($project);

    $this->actingAs($otherUser)
        ->postJson("/projects/{$project->slug}/solutions/{$solution->id}/publish")
        ->assertForbidden();
});

test('cannot publish solution without requirements', function () {
    $user = User::factory()->create();
    $solution = Solution::factory()
        ->for($user, 'user')
        ->create([
            'requirements' => null,
            'status' => 'draft'
        ]);
    $project = $solution->project;
    $user->projects()->attach($project);

    $this->actingAs($user)
        ->postJson("/projects/{$project->slug}/solutions/{$solution->id}/publish")
        ->assertUnprocessable()
        ->assertJson([
            'success' => false,
            'message' => 'Requirements must be completed before publishing solution.'
        ]);
});

test('can publish solution with requirements', function () {
    Queue::fake();

    $user = User::factory()->create();
    $solution = Solution::factory()
        ->requirementReady()
        ->for($user, 'user')
        ->create();
    $project = $solution->project;
    $user->projects()->attach($project);

    $this->actingAs($user)
        ->postJson("/projects/{$project->slug}/solutions/{$solution->id}/publish")
        ->assertSuccessful()
        ->assertJson([
            'success' => true,
            'solution_id' => $solution->id
        ]);

    Queue::assertPushed(\App\Jobs\GenerateTechnicalSolution::class);
});

test('cannot publish solution when generation is already in progress', function () {
    $user = User::factory()->create();
    $solution = Solution::factory()
        ->requirementReady()
        ->for($user, 'user')
        ->create();
    $project = $solution->project;
    $user->projects()->attach($project);

    // Simulate generation in progress
    Cache::put("solution_generation_{$solution->id}", [
        'status' => 'generating',
        'progress' => 50,
        'message' => 'Generating...'
    ], 600);

    $this->actingAs($user)
        ->postJson("/projects/{$project->slug}/solutions/{$solution->id}/publish")
        ->assertStatus(409)
        ->assertJson([
            'success' => false,
            'message' => 'Solution generation is already in progress.'
        ]);
});

test('can republish existing solution', function () {
    Queue::fake();

    $user = User::factory()->create();
    $solution = Solution::factory()
        ->solutionReady()
        ->for($user, 'user')
        ->create();
    $project = $solution->project;
    $user->projects()->attach($project);

    $this->actingAs($user)
        ->postJson("/projects/{$project->slug}/solutions/{$solution->id}/republish")
        ->assertSuccessful()
        ->assertJson([
            'success' => true,
            'solution_id' => $solution->id
        ]);

    Queue::assertPushed(\App\Jobs\GenerateTechnicalSolution::class);
});

test('cannot republish solution without requirements', function () {
    $user = User::factory()->create();
    $solution = Solution::factory()
        ->for($user, 'user')
        ->create([
            'requirements' => null,
            'status' => 'draft'
        ]);
    $project = $solution->project;
    $user->projects()->attach($project);

    $this->actingAs($user)
        ->postJson("/projects/{$project->slug}/solutions/{$solution->id}/republish")
        ->assertUnprocessable()
        ->assertJson([
            'success' => false,
            'message' => 'Requirements must exist before republishing solution.'
        ]);
});

test('progress endpoint returns idle when no generation in progress', function () {
    $user = User::factory()->create();
    $solution = Solution::factory()
        ->for($user, 'user')
        ->create();
    $project = $solution->project;
    $user->projects()->attach($project);

    $this->actingAs($user)
        ->getJson("/projects/{$project->slug}/solutions/{$solution->id}/progress")
        ->assertSuccessful()
        ->assertJson([
            'status' => 'idle',
            'progress' => 0,
            'message' => 'No generation in progress'
        ]);
});

test('progress endpoint returns cached progress data', function () {
    $user = User::factory()->create();
    $solution = Solution::factory()
        ->for($user, 'user')
        ->create();
    $project = $solution->project;
    $user->projects()->attach($project);

    $progressData = [
        'status' => 'generating',
        'progress' => 75,
        'message' => 'Generating comprehensive solution...'
    ];

    Cache::put("solution_generation_{$solution->id}", $progressData, 600);

    $this->actingAs($user)
        ->getJson("/projects/{$project->slug}/solutions/{$solution->id}/progress")
        ->assertSuccessful()
        ->assertJson($progressData);
});

test('users cannot view progress for solutions they do not own', function () {
    $owner = User::factory()->create();
    $otherUser = User::factory()->create();

    $solution = Solution::factory()
        ->for($owner, 'user')
        ->create();
    $project = $solution->project;

    $this->actingAs($otherUser)
        ->getJson("/projects/{$project->slug}/solutions/{$solution->id}/progress")
        ->assertForbidden();
});
