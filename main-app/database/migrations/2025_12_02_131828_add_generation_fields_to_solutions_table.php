<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('solutions', function (Blueprint $table) {
            // Modify status enum to include new generation statuses
            $table->enum('status', [
                'draft',
                'in_progress',
                'requirement_ready',
                'solution_ready',
                'generating_solution',
                'generation_failed',
                'approved',
                'rejected',
                'completed'
            ])->default('draft')->change();

            // Add generated_at timestamp
            $table->timestamp('generated_at')->nullable()->after('solution_approved_at');

            // Add metadata JSON column
            $table->json('metadata')->nullable()->after('generated_at');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('solutions', function (Blueprint $table) {
            // Revert status enum to original values
            $table->enum('status', [
                'draft',
                'in_progress',
                'requirement_ready',
                'solution_ready',
                'approved',
                'rejected',
                'completed'
            ])->default('draft')->change();

            // Drop added columns
            $table->dropColumn(['generated_at', 'metadata']);
        });
    }
};
