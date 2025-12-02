<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Conversation>
 */
class ConversationFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'user_id' => \App\Models\User::factory(),
            'project_id' => \App\Models\Project::factory(),
            'thread_id' => fake()->uuid(),
            'title' => fake()->sentence(),
            'status' => 'active',
            'summary' => fake()->paragraph(),
            'requirements' => null,
            'solution' => null,
            'message_count' => 0,
            'last_message_at' => now(),
        ];
    }
}
