<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Solution>
 */
class SolutionFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'conversation_id' => \App\Models\Conversation::factory(),
            'user_id' => \App\Models\User::factory(),
            'project_id' => \App\Models\Project::factory(),
            'title' => fake()->sentence(),
            'description' => fake()->paragraph(),
            'requirements' => fake()->paragraphs(3, true),
            'technical_solution' => null,
            'status' => 'draft',
            'requirement_approved_at' => null,
            'solution_approved_at' => null,
            'generated_at' => null,
            'metadata' => null,
        ];
    }

    /**
     * Indicate that the solution has requirements ready.
     */
    public function requirementReady(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'requirement_ready',
            'requirements' => fake()->paragraphs(5, true),
        ]);
    }

    /**
     * Indicate that the solution has technical solution ready.
     */
    public function solutionReady(): static
    {
        return $this->state(fn (array $attributes) => [
            'status' => 'solution_ready',
            'requirements' => fake()->paragraphs(5, true),
            'technical_solution' => fake()->paragraphs(20, true),
            'generated_at' => now(),
            'metadata' => [
                'model_used' => 'gpt-4o',
                'word_count' => 5000,
                'char_count' => 30000,
            ],
        ]);
    }
}
