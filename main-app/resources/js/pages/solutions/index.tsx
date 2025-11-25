import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import BackButton from '@/components/back-button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link } from '@inertiajs/react';
import { CheckCircle, Clock, Code, FileText, Lightbulb } from 'lucide-react';

interface SolutionsProps {
    project: Project;
}

// Mock data - will be replaced with real data from DB later
const mockSolutions = [
    {
        id: '1',
        title: 'User Authentication Implementation',
        description: 'JWT-based authentication system with refresh tokens',
        status: 'implemented' as const,
        category: 'authentication',
        acceptedAt: new Date(Date.now() - 1000 * 60 * 60 * 48), // 2 days ago
        code: true,
        documentation: true,
    },
    {
        id: '2',
        title: 'Database Migration Strategy',
        description: 'Optimized database schema with proper indexing',
        status: 'accepted' as const,
        category: 'database',
        acceptedAt: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
        code: false,
        documentation: true,
    },
    {
        id: '3',
        title: 'API Rate Limiting Solution',
        description: 'Redis-based rate limiting for API endpoints',
        status: 'in-progress' as const,
        category: 'api',
        acceptedAt: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
        code: true,
        documentation: false,
    },
];

const statusConfig = {
    implemented: {
        label: 'Implemented',
        color: 'bg-green-500/10 text-green-700 dark:text-green-400',
        icon: CheckCircle,
    },
    accepted: {
        label: 'Accepted',
        color: 'bg-blue-500/10 text-blue-700 dark:text-blue-400',
        icon: Lightbulb,
    },
    'in-progress': {
        label: 'In Progress',
        color: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400',
        icon: Clock,
    },
};

export default function Solutions({ project }: SolutionsProps) {
    const breadcrumbs: BreadcrumbItem[] = [
        {
            title: project.name,
            href: `/projects/${project.slug}/home`,
        },
        {
            title: 'Solutions',
            href: `/projects/${project.slug}/solutions`,
        },
    ];

    const formatDate = (date: Date) => {
        return date.toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={`${project.name} - Solutions`} />
            <div className="flex h-full flex-1 flex-col gap-6 p-4">
                <div className="mb-2">
                    <BackButton label="Back to Project" />
                </div>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Solutions</h1>
                        <p className="text-muted-foreground">
                            Your accepted solutions for {project.name}
                        </p>
                    </div>
                    <Button asChild>
                        <Link href={`/projects/${project.slug}/chat`}>
                            <Lightbulb className="mr-2 h-4 w-4" />
                            Get New Solution
                        </Link>
                    </Button>
                </div>

                {mockSolutions.length === 0 ? (
                    <Card className="flex flex-col items-center justify-center p-12">
                        <Lightbulb className="mb-4 h-12 w-12 text-muted-foreground" />
                        <h3 className="mb-2 text-lg font-semibold">No solutions yet</h3>
                        <p className="mb-4 text-center text-muted-foreground">
                            Chat with the AI to get solutions for your project
                        </p>
                        <Button asChild>
                            <Link href={`/projects/${project.slug}/chat`}>
                                Start Chatting
                            </Link>
                        </Button>
                    </Card>
                ) : (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {mockSolutions.map((solution) => {
                            const StatusIcon = statusConfig[solution.status].icon;
                            return (
                                <Card
                                    key={solution.id}
                                    className="cursor-pointer transition-shadow hover:shadow-md"
                                    onClick={() => {
                                        // Navigate to solution detail (to be implemented)
                                        console.log('View solution:', solution.id);
                                    }}
                                >
                                    <CardHeader>
                                        <div className="mb-2 flex items-start justify-between">
                                            <Badge
                                                variant="secondary"
                                                className={statusConfig[solution.status].color}
                                            >
                                                <StatusIcon className="mr-1 h-3 w-3" />
                                                {statusConfig[solution.status].label}
                                            </Badge>
                                        </div>
                                        <CardTitle className="line-clamp-2">
                                            {solution.title}
                                        </CardTitle>
                                        <CardDescription className="line-clamp-3">
                                            {solution.description}
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-3">
                                            <div className="flex gap-2">
                                                <Badge
                                                    variant="outline"
                                                    className="text-xs capitalize"
                                                >
                                                    {solution.category}
                                                </Badge>
                                            </div>
                                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                                {solution.code && (
                                                    <div className="flex items-center gap-1">
                                                        <Code className="h-4 w-4" />
                                                        <span>Code</span>
                                                    </div>
                                                )}
                                                {solution.documentation && (
                                                    <div className="flex items-center gap-1">
                                                        <FileText className="h-4 w-4" />
                                                        <span>Docs</span>
                                                    </div>
                                                )}
                                            </div>
                                            <div className="text-xs text-muted-foreground">
                                                Accepted {formatDate(solution.acceptedAt)}
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            );
                        })}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
