<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Inertia\Inertia;
use Inertia\Response;

class LearnedKnowledgeController extends Controller
{
    /**
     * Display a listing of learned knowledge pending review.
     */
    public function index(): Response
    {
        $kbAdminUrl = env('KB_ADMIN_URL', 'http://kb-admin:8000');
        
        try {
            // Fetch pending knowledge from kb-admin
            $response = Http::timeout(5)->get("{$kbAdminUrl}/api/learning/pending");
            
            $pendingKnowledge = $response->successful() ? $response->json() : [];
            
        } catch (\Exception $e) {
            $pendingKnowledge = [];
            // In a real app we might flash an error
        }

        return Inertia::render('admin/learned-knowledge/index', [
            'pendingKnowledge' => $pendingKnowledge,
        ]);
    }

    /**
     * Review knowledge (approve/reject).
     */
    public function review(Request $request, int $id)
    {
        $request->validate([
            'status' => 'required|in:approved,rejected',
        ]);

        $kbAdminUrl = env('KB_ADMIN_URL', 'http://kb-admin:8000');
        $user = $request->user();

        try {
            $response = Http::timeout(10)->post("{$kbAdminUrl}/api/learning/{$id}/review", [
                'status' => $request->status,
                'reviewed_by' => $user->name,
            ]);

            if ($response->successful()) {
                return redirect()->back()->with('success', "Knowledge {$request->status} successfully.");
            }

            return redirect()->back()->with('error', "Failed to review knowledge: " . $response->body());

        } catch (\Exception $e) {
            return redirect()->back()->with('error', "Error communicating with KB Service: " . $e->getMessage());
        }
    }
}
