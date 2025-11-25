import HeadingSmall from '@/components/heading-small';
import InputError from '@/components/input-error';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import AppLayout from '@/layouts/app-layout';
import SettingsLayout from '@/layouts/settings/layout';
import { type BreadcrumbItem } from '@/types';
import { Form, Head } from '@inertiajs/react';
import { useState } from 'react';
import { edit } from '@/routes/ai';

interface AiSetting {
    provider: 'openai' | 'anthropic';
    has_api_key: boolean;
}

interface AiProps {
    ai_setting: AiSetting | null;
}

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'AI Settings',
        href: edit().url,
    },
];

export default function Ai({ ai_setting }: AiProps) {
    const [provider, setProvider] = useState(ai_setting?.provider || 'openai');

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title="AI Settings" />

            <SettingsLayout>
                <div className="space-y-6">
                    <HeadingSmall
                        title="AI Configuration"
                        description="Configure your AI provider and API key"
                    />

                    <Form
                        action="/settings/ai"
                        method="patch"
                        options={{
                            preserveScroll: true,
                        }}
                        className="space-y-6"
                    >
                        {({ errors, processing, wasSuccessful }) => (
                            <>
                                <div>
                                    <Label htmlFor="provider">AI Provider</Label>
                                    <input type="hidden" name="provider" value={provider} />
                                    <Select value={provider} onValueChange={setProvider}>
                                        <SelectTrigger id="provider" className="mt-2">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="openai">OpenAI (ChatGPT, GPT-4, etc.)</SelectItem>
                                            <SelectItem value="anthropic">Anthropic (Claude)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <InputError className="mt-2" message={errors.provider} />
                                </div>

                                <div>
                                    <Label htmlFor="api_key">
                                        API Key
                                        {ai_setting?.has_api_key && (
                                            <span className="ml-2 text-xs text-muted-foreground">
                                                (Leave blank to keep current key)
                                            </span>
                                        )}
                                    </Label>
                                    <Input
                                        id="api_key"
                                        name="api_key"
                                        type="password"
                                        className="mt-2"
                                        placeholder={
                                            ai_setting?.has_api_key
                                                ? '••••••••••••••••••••••••'
                                                : 'Enter your API key'
                                        }
                                        autoComplete="off"
                                    />
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Your API key is encrypted and stored securely. It will never be
                                        displayed in full.
                                    </p>
                                    <InputError className="mt-2" message={errors.api_key} />
                                </div>

                                <div className="flex items-center gap-4">
                                    <Button disabled={processing} data-test="update-ai-button">
                                        {processing ? 'Saving...' : 'Save AI Settings'}
                                    </Button>

                                    {wasSuccessful && (
                                        <p className="text-sm text-green-600">
                                            AI settings updated successfully.
                                        </p>
                                    )}
                                </div>
                            </>
                        )}
                    </Form>

                    <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-900 dark:bg-yellow-950">
                        <h4 className="mb-2 font-medium text-yellow-800 dark:text-yellow-200">
                            Important Information
                        </h4>
                        <ul className="list-disc space-y-1 pl-5 text-sm text-yellow-700 dark:text-yellow-300">
                            <li>
                                Get your OpenAI API key from{' '}
                                <a
                                    href="https://platform.openai.com/api-keys"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="underline"
                                >
                                    platform.openai.com/api-keys
                                </a>
                            </li>
                            <li>
                                Get your Anthropic API key from{' '}
                                <a
                                    href="https://console.anthropic.com/settings/keys"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="underline"
                                >
                                    console.anthropic.com/settings/keys
                                </a>
                            </li>
                            <li>Never share your API keys with anyone</li>
                            <li>
                                Usage charges apply directly to your account with the provider
                            </li>
                        </ul>
                    </div>
                </div>
            </SettingsLayout>
        </AppLayout>
    );
}
