<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class ChatFileController extends Controller
{
    /**
     * Handle file uploads for chat messages
     */
    public function upload(Request $request, $project)
    {
        $request->validate([
            'files' => 'required|array',
            'files.*' => 'file|max:10240|mimes:pdf,doc,docx,txt', // Max 10MB per file
        ]);

        $attachments = [];

        foreach ($request->file('files') as $file) {
            // Generate unique filename
            $filename = Str::random(40) . '.' . $file->getClientOriginalExtension();
            
            // Store in storage/app/chat-files/{project_slug}/
            $path = $file->storeAs(
                "chat-files/{$project}",
                $filename,
                'local'
            );

            $attachments[] = [
                'id' => Str::uuid()->toString(),
                'name' => $file->getClientOriginalName(),
                'size' => $file->getSize(),
                'type' => $file->getMimeType(),
                'url' => route('chat.file.download', [
                    'project' => $project,
                    'filename' => $filename
                ]),
            ];
        }

        return response()->json([
            'success' => true,
            'attachments' => $attachments,
        ]);
    }

    /**
     * Download/view a chat file
     */
    public function download($project, $filename)
    {
        $path = "chat-files/{$project}/{$filename}";

        if (!Storage::exists($path)) {
            abort(404);
        }

        return Storage::download($path);
    }
}
