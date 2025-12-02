<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Solution extends Model
{
    use HasFactory;
    protected $fillable = [
        'conversation_id',
        'user_id',
        'project_id',
        'title',
        'description',
        'requirements',
        'technical_solution',
        'status',
        'requirement_approved_at',
        'solution_approved_at',
        'generated_at',
        'metadata',
    ];

    protected $casts = [
        'requirement_approved_at' => 'datetime',
        'solution_approved_at' => 'datetime',
        'generated_at' => 'datetime',
        'metadata' => 'array',
    ];

    /**
     * Get the conversation that owns the solution.
     */
    public function conversation(): BelongsTo
    {
        return $this->belongsTo(Conversation::class);
    }

    /**
     * Get the user that owns the solution.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the project associated with the solution.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    /**
     * Scope a query to only include solutions for a specific user.
     */
    public function scopeForUser($query, $userId)
    {
        return $query->where('user_id', $userId);
    }

    /**
     * Scope a query to only include solutions with a specific status.
     */
    public function scopeWithStatus($query, $status)
    {
        return $query->where('status', $status);
    }
}
