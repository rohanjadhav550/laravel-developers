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
        Schema::create('solutions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('conversation_id')->constrained()->onDelete('cascade');
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->foreignId('project_id')->nullable()->constrained()->onDelete('set null');
            $table->string('title');
            $table->text('description')->nullable();
            $table->longText('requirements')->nullable();
            $table->longText('technical_solution')->nullable();
            $table->enum('status', ['draft', 'in_progress', 'requirement_ready', 'solution_ready', 'approved', 'rejected', 'completed'])->default('draft');
            $table->timestamp('requirement_approved_at')->nullable();
            $table->timestamp('solution_approved_at')->nullable();
            $table->timestamps();

            $table->index(['user_id', 'status']);
            $table->index('conversation_id');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('solutions');
    }
};
