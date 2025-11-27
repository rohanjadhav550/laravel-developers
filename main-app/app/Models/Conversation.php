<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Conversation extends Model
{
    protected $fillable = [
        'user_id',
        'thread_id',
        'title',
        'project_id',
        'status',
        'summary',
        'message_count',
        'last_message_at',
    ];

    protected $casts = [
        'last_message_at' => 'datetime',
    ];

    /**
     * Get the user that owns the conversation.
     */
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Get the project associated with the conversation.
     */
    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }
}
