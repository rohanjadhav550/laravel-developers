<?php

namespace App\Http\Controllers\Settings;

use App\Http\Controllers\Controller;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;
use Inertia\Inertia;
use Inertia\Response;

class AiController extends Controller
{
    /**
     * Show the AI settings form.
     */
    public function edit(Request $request): Response
    {
        $aiSetting = $request->user()->aiSetting;

        return Inertia::render('settings/ai', [
            'ai_setting' => $aiSetting ? [
                'provider' => $aiSetting->provider,
                'has_api_key' => !empty($aiSetting->api_key),
            ] : null,
        ]);
    }

    /**
     * Update the user's AI settings.
     */
    public function update(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'provider' => ['required', Rule::in(['openai', 'anthropic'])],
            'api_key' => ['nullable', 'string', 'min:10'],
        ]);

        $aiSetting = $request->user()->aiSetting()->firstOrNew();

        $aiSetting->provider = $validated['provider'];

        if (!empty($validated['api_key'])) {
            $aiSetting->api_key = $validated['api_key'];
        }

        $aiSetting->save();

        return back()->with('success', 'AI settings updated successfully.');
    }
}
