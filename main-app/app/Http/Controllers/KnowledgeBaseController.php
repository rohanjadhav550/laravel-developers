<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Inertia\Inertia;
use Inertia\Response;

class KnowledgeBaseController extends Controller
{
    protected string $kbAdminUrl;

    public function __construct()
    {
        $this->kbAdminUrl = env('KB_ADMIN_URL', 'http://kb-admin:8000');
    }

    /**
     * Display a listing of knowledge bases.
     */
    public function index(): Response
    {
        $response = Http::timeout(5)->get("{$this->kbAdminUrl}/api/kb/");
        $kbs = $response->successful() ? $response->json()['items'] : [];

        // Also fetch pending learned knowledge count
        $statsResponse = Http::timeout(3)->get("{$this->kbAdminUrl}/api/learning/pending");
        $pendingCount = $statsResponse->successful() ? count($statsResponse->json()) : 0;

        return Inertia::render('admin/knowledge/index', [
            'knowledgeBases' => $kbs,
            'pendingReviewsCount' => $pendingCount,
        ]);
    }

    /**
     * Display the specified knowledge base and its documents.
     */
    public function show(int $id, Request $request): Response
    {
        $kbResponse = Http::timeout(5)->get("{$this->kbAdminUrl}/api/kb/{$id}");
        
        if (!$kbResponse->successful()) {
            abort(404, 'Knowledge Base not found');
        }

        $page = $request->query('page', 1);
        $search = $request->query('search', '');
        
        // Fetch documents
        $docsResponse = Http::timeout(10)->get("{$this->kbAdminUrl}/api/kb/{$id}/documents", [
            'page' => $page,
            'search' => $search
        ]);
        
        $documents = $docsResponse->successful() ? $docsResponse->json() : ['items' => [], 'total' => 0];

        // Fetch stats
        $statsResponse = Http::timeout(5)->get("{$this->kbAdminUrl}/api/kb/{$id}/status");
        $stats = $statsResponse->successful() ? $statsResponse->json() : null;

        return Inertia::render('admin/knowledge/show', [
            'kb' => $kbResponse->json(),
            'documents' => $documents,
            'stats' => $stats,
        ]);
    }

    /**
     * Upload a document to the knowledge base.
     */
    public function upload(int $id, Request $request)
    {
        $request->validate([
            'file' => 'required|file|mimes:txt,md,pdf|max:10240', // 10MB max
            'title' => 'nullable|string|max:255',
        ]);

        $file = $request->file('file');
        
        $response = Http::timeout(30)
            ->attach('file', file_get_contents($file->path()), $file->getClientOriginalName())
            ->post("{$this->kbAdminUrl}/api/kb/{$id}/documents/upload", [
                'title' => $request->input('title'),
            ]);

        if ($response->successful()) {
            return redirect()->back()->with('success', 'Document uploaded successfully.');
        }

        return redirect()->back()->with('error', 'Failed to upload document: ' . $response->body());
    }

    /**
     * Delete a document.
     */
    public function destroyDocument(int $id, int $docId)
    {
        $response = Http::timeout(10)->delete("{$this->kbAdminUrl}/api/kb/{$id}/documents/{$docId}");

        if ($response->successful()) {
            return redirect()->back()->with('success', 'Document deleted successfully.');
        }

        return redirect()->back()->with('error', 'Failed to delete document.');
    }

    /**
     * Trigger manual vectorization.
     */
    public function vectorize(int $id)
    {
         // Send proper JSON request with explicit headers
         $response = Http::timeout(60)
             ->withHeaders(['Content-Type' => 'application/json', 'Accept' => 'application/json'])
             ->post("{$this->kbAdminUrl}/api/kb/{$id}/vectorize", [
                 // Empty body is ok, but must be valid JSON
             ]);

         if ($response->successful()) {
             return redirect()->back()->with('success', 'Vectorization triggered successfully.');
         }

         // Log the error for debugging
         \Log::error("Vectorization failed for KB {$id}", [
             'status' => $response->status(),
             'body' => $response->body()
         ]);

         return redirect()->back()->with('error', 'Failed to trigger vectorization: ' . $response->body());
    }
}
