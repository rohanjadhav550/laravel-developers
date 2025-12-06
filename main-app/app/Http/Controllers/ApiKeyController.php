<?php

namespace App\Http\Controllers;

use App\Models\AiSetting;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ApiKeyController extends Controller
{
    /**
     * Get API key for a specific provider (for microservices)
     * This endpoint is used by kb-admin and other services to retrieve API keys
     */
    public function getApiKey(Request $request, string $provider)
    {
        // Validate provider
        $validProviders = ['openai', 'anthropic', 'gemini'];
        if (!in_array($provider, $validProviders)) {
            return response()->json([
                'error' => 'Invalid provider',
                'valid_providers' => $validProviders
            ], 400);
        }

        // Get the first available API key for this provider
        // You might want to add user-specific logic here
        $setting = AiSetting::where('provider', $provider)
            ->whereNotNull('api_key')
            ->first();

        if (!$setting) {
            return response()->json([
                'error' => 'No API key found for provider: ' . $provider,
                'provider' => $provider,
                'has_key' => false
            ], 404);
        }

        // Return the decrypted API key
        return response()->json([
            'provider' => $provider,
            'api_key' => $setting->api_key, // Automatically decrypted by Laravel
            'has_key' => true
        ]);
    }

    /**
     * Check if API key exists for a provider (without exposing the key)
     */
    public function checkApiKey(string $provider)
    {
        $validProviders = ['openai', 'anthropic', 'gemini'];
        if (!in_array($provider, $validProviders)) {
            return response()->json([
                'error' => 'Invalid provider'
            ], 400);
        }

        $exists = AiSetting::where('provider', $provider)
            ->whereNotNull('api_key')
            ->exists();

        return response()->json([
            'provider' => $provider,
            'has_key' => $exists
        ]);
    }
}
