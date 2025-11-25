import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import BackButton from '@/components/back-button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head } from '@inertiajs/react';
import { Send, Sparkles, Paperclip, X, FileText, Edit2 } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface ChatProps {
    project: Project;
}

interface Attachment {
    id: string;
    name: string;
    size: number;
    type: string;
    url: string;
}

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    attachments?: Attachment[];
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
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const [editingMessageId, setEditingMessageId] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

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

    const formatFileSize = (bytes: number) => {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
        ];

        const validFiles = files.filter((file) => {
            const isValidType = allowedTypes.includes(file.type) ||
                file.name.endsWith('.doc') ||
                file.name.endsWith('.docx') ||
                file.name.endsWith('.pdf') ||
                file.name.endsWith('.txt');

            if (!isValidType) {
                alert(`File "${file.name}" is not allowed. Only PDF, Word, and TXT files are supported.`);
                return false;
            }
            return true;
        });

        setAttachedFiles((prev) => [...prev, ...validFiles]);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const removeFile = (index: number) => {
        setAttachedFiles((prev) => prev.filter((_, i) => i !== index));
    };

    const uploadFiles = async (files: File[]): Promise<Attachment[]> => {
        const formData = new FormData();
        files.forEach((file) => {
            formData.append('files[]', file);
        });
        formData.append('project_slug', project.slug);

        try {
            const response = await fetch(`/projects/${project.slug}/chat/upload`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRF-TOKEN': (document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement)?.content || '',
                },
            });

            if (!response.ok) {
                throw new Error('Upload failed');
            }

            const data = await response.json();
            return data.attachments;
        } catch (error) {
            console.error('File upload error:', error);
            alert('Failed to upload files. Please try again.');
            return [];
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() && attachedFiles.length === 0) return;

        const uploadedAttachments = attachedFiles.length > 0 ? await uploadFiles(attachedFiles) : [];

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date(),
            attachments: uploadedAttachments.length > 0 ? uploadedAttachments : undefined,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setAttachedFiles([]);
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

    const handleRevertToMessage = (messageId: string) => {
        const messageIndex = messages.findIndex((m) => m.id === messageId);
        if (messageIndex !== -1) {
            // Set input to the message content
            setInput(messages[messageIndex].content);

            // Revert conversation to the point BEFORE this message
            setMessages((prev) => prev.slice(0, messageIndex));
            setEditingMessageId(null);
        }
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
                        <h1 className="text-xl font-semibold">AI Assistant</h1>
                        <p className="text-sm text-muted-foreground">Get help with your ideas</p>
                    </div>
                </div>

                <Card className="flex flex-1 flex-col overflow-hidden">
                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-4">
                        <div className="mx-auto max-w-3xl space-y-4">
                            {messages.map((message, index) => (
                                <div
                                    key={message.id}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`group relative max-w-[80%] rounded-lg p-3 ${message.role === 'user'
                                            ? 'bg-primary text-primary-foreground'
                                            : 'bg-muted'
                                            }`}
                                    >
                                        {/* Edit/Revert button (only show on user messages and not the last message) */}
                                        {message.role === 'user' && index < messages.length - 1 && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="absolute -left-10 top-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100"
                                                onClick={() => handleRevertToMessage(message.id)}
                                                title="Revert conversation to this point"
                                            >
                                                <Edit2 className="h-4 w-4 text-muted-foreground" />
                                            </Button>
                                        )}

                                        <div className="mb-1 flex items-center gap-2">
                                            <span className="text-xs font-medium">
                                                {message.role === 'user' ? 'You' : 'Assistant'}
                                            </span>
                                            <span className="text-xs opacity-70">
                                                {message.timestamp.toLocaleTimeString([], {
                                                    hour: '2-digit',
                                                    minute: '2-digit',
                                                })}
                                            </span>
                                        </div>
                                        <p className="whitespace-pre-wrap">{message.content}</p>

                                        {/* Display attachments */}
                                        {message.attachments && message.attachments.length > 0 && (
                                            <div className="mt-2 space-y-1">
                                                {message.attachments.map((attachment) => (
                                                    <a
                                                        key={attachment.id}
                                                        href={attachment.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="flex items-center gap-2 rounded bg-background/20 p-2 text-sm hover:bg-background/30"
                                                    >
                                                        <FileText className="h-4 w-4" />
                                                        <span className="flex-1 truncate">{attachment.name}</span>
                                                        <span className="text-xs opacity-70">
                                                            {formatFileSize(attachment.size)}
                                                        </span>
                                                    </a>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}

                            {isTyping && (
                                <div className="flex justify-start">
                                    <div className="max-w-[80%] rounded-lg bg-muted p-3">
                                        <div className="flex items-center gap-2">
                                            <div className="flex gap-1">
                                                <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]"></div>
                                                <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]"></div>
                                                <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground"></div>
                                            </div>
                                            <span className="text-xs text-muted-foreground">Assistant is typing...</span>
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
                            {/* Attached files display */}
                            {attachedFiles.length > 0 && (
                                <div className="mb-2 flex flex-wrap gap-2">
                                    {attachedFiles.map((file, index) => (
                                        <div
                                            key={index}
                                            className="flex items-center gap-2 rounded-md border bg-muted px-3 py-2 text-sm"
                                        >
                                            <FileText className="h-4 w-4" />
                                            <span className="max-w-[200px] truncate">{file.name}</span>
                                            <span className="text-xs text-muted-foreground">
                                                {formatFileSize(file.size)}
                                            </span>
                                            <button
                                                type="button"
                                                onClick={() => removeFile(index)}
                                                className="ml-1 rounded-full p-0.5 hover:bg-background"
                                            >
                                                <X className="h-3 w-3" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}

                            <div className="flex gap-2">
                                {/* File upload button */}
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    multiple
                                    accept=".pdf,.doc,.docx,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                                    onChange={handleFileSelect}
                                    className="hidden"
                                />
                                <Button
                                    type="button"
                                    variant="outline"
                                    size="icon"
                                    onClick={() => fileInputRef.current?.click()}
                                    disabled={isTyping}
                                    title="Attach file (PDF, Word, TXT)"
                                >
                                    <Paperclip className="h-4 w-4" />
                                </Button>

                                <Input
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Type your message..."
                                    className="flex-1"
                                    disabled={isTyping}
                                />
                                <Button type="submit" disabled={(!input.trim() && attachedFiles.length === 0) || isTyping}>
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
