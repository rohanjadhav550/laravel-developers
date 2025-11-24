<?php

namespace App\Actions\Fortify;

use App\Models\Project;
use App\Models\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Laravel\Fortify\Contracts\CreatesNewUsers;

class CreateNewUser implements CreatesNewUsers
{
    use PasswordValidationRules;

    /**
     * Validate and create a newly registered user.
     *
     * @param  array<string, string>  $input
     */
    public function create(array $input): User
    {
        Validator::make($input, [
            'name' => ['required', 'string', 'max:255'],
            'email' => [
                'required',
                'string',
                'email',
                'max:255',
                Rule::unique(User::class),
            ],
            'password' => $this->passwordRules(),
        ])->validate();

        return DB::transaction(function () use ($input) {
            $user = User::create([
                'name' => $input['name'],
                'email' => $input['email'],
                'password' => $input['password'],
            ]);

            $this->createDefaultProject($user);

            return $user;
        });
    }

    /**
     * Create a default project for the newly registered user.
     */
    protected function createDefaultProject(User $user): Project
    {
        $project = Project::create([
            'name' => $user->name . "'s Project",
            'slug' => Str::slug($user->name) . '-' . Str::random(6),
            'owner_id' => $user->id,
        ]);

        $project->users()->attach($user->id, ['role' => 'owner']);

        return $project;
    }
}
