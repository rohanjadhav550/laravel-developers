<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\AiSetting;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class AiSettingsApiController extends Controller
{
    /**
     * Get decrypted AI settings for a user.
     * This is an internal API used by the idea-agent microservice.
     */
    public function getSettings(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'user_id' => ['required', 'integer', 'exists:users,id'],
        ]);

        $aiSetting = AiSetting::where('user_id', $validated['user_id'])->first();

        if (!$aiSetting) {
            return response()->json([
                'success' => false,
                'message' => 'AI settings not found for this user.',
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => [
                'provider' => $aiSetting->provider,
                'api_key' => $aiSetting->api_key, // Laravel will auto-decrypt due to 'encrypted' cast
            ],
        ]);
    }
}
