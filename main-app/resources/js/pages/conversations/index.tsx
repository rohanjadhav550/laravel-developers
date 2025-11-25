import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import BackButton from '@/components/back-button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link } from '@inertiajs/react';
import { MessageSquare, Plus } from 'lucide-react';

interface ConversationsProps {
    project: Project;
}

// Mock data - will be replaced with real data from DB later
const mockConversations = [
    {
        id: '1',
        title: 'Building a user authentication system',
        preview: 'I need help implementing secure user authentication...',
        messageCount: 12,
        lastMessageAt: new Date(Date.now() - 1000 * 60 * 30), // 30 min ago
    },
    {
        id: '2',
        title: 'Database schema design discussion',
        preview: 'What would be the best approach for designing...',
        messageCount: 8,
        lastMessageAt: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    },
    {
        id: '3',
        title: 'API integration questions',
        preview: 'How should I handle API rate limiting and...',
        messageCount: 15,
        lastMessageAt: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    },
];

export default function Conversations({ project }: ConversationsProps) {
    const breadcrumbs: BreadcrumbItem[] = [
        {
            title: project.name,
            href: `/projects/${project.slug}/home`,
        },
        {
            title: 'Conversations',
            href: `/projects/${project.slug}/conversations`,
        },
    ];

    const formatTime = (date: Date) => {
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    };

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={`${project.name} - Conversations`} />
            <div className="flex h-full flex-1 flex-col gap-6 p-4">
                <div className="mb-2">
                    <BackButton label="Back to Project" />
                </div>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Conversations</h1>
                        <p className="text-muted-foreground">
                            View your chat history for {project.name}
                        </p>
                    </div>
                    <Button asChild>
                        <Link href={`/projects/${project.slug}/chat`}>
                            <Plus className="mr-2 h-4 w-4" />
                            New Chat
                        </Link>
                    </Button>
                </div>

                {mockConversations.length === 0 ? (
                    <Card className="flex flex-col items-center justify-center p-12">
                        <MessageSquare className="mb-4 h-12 w-12 text-muted-foreground" />
                        <h3 className="mb-2 text-lg font-semibold">No conversations yet</h3>
                        <p className="mb-4 text-center text-muted-foreground">
                            Start a new conversation to get help with your project
                        </p>
                        <Button asChild>
                            <Link href={`/projects/${project.slug}/chat`}>
                                Start Chatting
                            </Link>
                        </Button>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {mockConversations.map((conversation) => (
                            <Card
                                key={conversation.id}
                                className="cursor-pointer transition-shadow hover:shadow-md"
                                onClick={() => {
                                    // Navigate to specific conversation (to be implemented)
                                    window.location.href = `/projects/${project.slug}/chat?conversation=${conversation.id}`;
                                }}
                            >
                                <CardHeader>
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <CardTitle className="mb-1 flex items-center gap-2">
                                                <MessageSquare className="h-5 w-5 text-primary" />
                                                {conversation.title}
                                            </CardTitle>
                                            <CardDescription className="line-clamp-2">
                                                {conversation.preview}
                                            </CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                                        <span>{conversation.messageCount} messages</span>
                                        <span>{formatTime(conversation.lastMessageAt)}</span>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
