import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import BackButton from '@/components/back-button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head } from '@inertiajs/react';
import { Send, Sparkles } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface ChatProps {
    project: Project;
}

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

export default function Chat({ project }: ChatProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: `Hello! I'm here to help you with ${project.name}. Tell me your idea and I'll assist you in bringing it to life.`,
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const breadcrumbs: BreadcrumbItem[] = [
        {
            title: project.name,
            href: `/projects/${project.slug}/home`,
        },
        {
            title: 'Chat',
            href: `/projects/${project.slug}/chat`,
        },
    ];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        // Simulate AI response (replace with actual API call later)
        setTimeout(() => {
            const aiMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: `I understand you want to: "${userMessage.content}". This is a placeholder response. In the future, this will be connected to an AI agent to help you develop your idea.`,
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, aiMessage]);
            setIsTyping(false);
        }, 1500);
    };

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={`${project.name} - Chat`} />
            <div className="flex h-full flex-1 flex-col p-4">
                <div className="mb-4">
                    <BackButton label="Back to Project" />
                </div>
                <div className="mb-4 flex items-center gap-3">
                    <div className="rounded-full bg-gradient-to-r from-purple-500 to-blue-500 p-2">
                        <Sparkles className="h-5 w-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold">AI Chat Assistant</h1>
                        <p className="text-muted-foreground">
                            Tell me your idea for {project.name}
                        </p>
                    </div>
                </div>

                <Card className="flex flex-1 flex-col overflow-hidden">
                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-4">
                        <div className="mx-auto max-w-3xl space-y-4">
                            {messages.map((message) => (
                                <div
                                    key={message.id}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] rounded-2xl px-4 py-3 ${message.role === 'user'
                                            ? 'bg-primary text-primary-foreground'
                                            : 'bg-muted'
                                            }`}
                                    >
                                        <p className="whitespace-pre-wrap break-words">
                                            {message.content}
                                        </p>
                                        <p
                                            className={`mt-1 text-xs ${message.role === 'user'
                                                ? 'text-primary-foreground/70'
                                                : 'text-muted-foreground'
                                                }`}
                                        >
                                            {message.timestamp.toLocaleTimeString([], {
                                                hour: '2-digit',
                                                minute: '2-digit',
                                            })}
                                        </p>
                                    </div>
                                </div>
                            ))}

                            {isTyping && (
                                <div className="flex justify-start">
                                    <div className="max-w-[80%] rounded-2xl bg-muted px-4 py-3">
                                        <div className="flex space-x-2">
                                            <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground"></div>
                                            <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:0.2s]"></div>
                                            <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:0.4s]"></div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    {/* Input Area */}
                    <div className="border-t bg-background/95 p-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                        <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
                            <div className="flex gap-2">
                                <Input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Type your message..."
                                    className="flex-1"
                                    disabled={isTyping}
                                />
                                <Button type="submit" disabled={!input.trim() || isTyping}>
                                    <Send className="h-4 w-4" />
                                </Button>
                            </div>
                        </form>
                    </div>
                </Card>
            </div>
        </AppLayout>
    );
}
