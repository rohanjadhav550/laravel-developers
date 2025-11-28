import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import BackButton from '@/components/back-button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link } from '@inertiajs/react';
import { CheckCircle, Clock, Code, FileText, Lightbulb, XCircle } from 'lucide-react';

interface Solution {
    id: number;
    conversation_id: number;
    user_id: number;
    project_id: number | null;
    title: string;
    description: string | null;
    requirements: string | null;
    technical_solution: string | null;
    status: 'draft' | 'in_progress' | 'requirement_ready' | 'solution_ready' | 'approved' | 'rejected' | 'completed';
    requirement_approved_at: string | null;
    solution_approved_at: string | null;
    created_at: string;
    updated_at: string;
}

interface SolutionsProps {
    project: Project;
    solutions: {
        data: Solution[];
        current_page: number;
        last_page: number;
        per_page: number;
        total: number;
    };
    filters: {
        search: string;
        status: string;
        per_page: number;
    };
    statuses: Record<string, string>;
}

const statusConfig: Record<string, { label: string; color: string; icon: any }> = {
    draft: {
        label: 'Draft',
        color: 'bg-gray-500/10 text-gray-700 dark:text-gray-400',
        icon: FileText,
    },
    in_progress: {
        label: 'In Progress',
        color: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400',
        icon: Clock,
    },
    requirement_ready: {
        label: 'Requirement Ready',
        color: 'bg-blue-500/10 text-blue-700 dark:text-blue-400',
        icon: FileText,
    },
    solution_ready: {
        label: 'Solution Ready',
        color: 'bg-purple-500/10 text-purple-700 dark:text-purple-400',
        icon: Code,
    },
    approved: {
        label: 'Approved',
        color: 'bg-green-500/10 text-green-700 dark:text-green-400',
        icon: CheckCircle,
    },
    rejected: {
        label: 'Rejected',
        color: 'bg-red-500/10 text-red-700 dark:text-red-400',
        icon: XCircle,
    },
    completed: {
        label: 'Completed',
        color: 'bg-green-500/10 text-green-700 dark:text-green-400',
        icon: CheckCircle,
    },
};

export default function Solutions({ project, solutions, filters, statuses }: SolutionsProps) {
    const breadcrumbs: BreadcrumbItem[] = [
        {
            title: project?.name || 'Project',
            href: `/projects/${project?.slug || 'unknown'}/home`,
        },
        {
            title: 'Solutions',
            href: `/projects/${project?.slug || 'unknown'}/solutions`,
        },
    ];

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
        });
    };

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={`${project?.name || 'Solutions'} - Solutions`} />
            <div className="flex h-full flex-1 flex-col gap-6 p-4">
                <div className="mb-2">
                    <BackButton label="Back to Project" />
                </div>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Solutions</h1>
                        <p className="text-muted-foreground">
                            Your solutions for {project?.name || 'this project'}
                        </p>
                    </div>
                    <Button asChild>
                        <Link href={`/projects/${project?.slug || 'unknown'}/chat`}>
                            <Lightbulb className="mr-2 h-4 w-4" />
                            Get New Solution
                        </Link>
                    </Button>
                </div>

                {solutions.data.length === 0 ? (
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
                        {solutions.data.map((solution) => {
                            const StatusIcon = statusConfig[solution.status]?.icon || FileText;
                            return (
                                <Link
                                    key={solution.id}
                                    href={`/projects/${project?.slug || 'unknown'}/solutions/${solution.id}`}
                                >
                                    <Card className="cursor-pointer transition-shadow hover:shadow-md">
                                        <CardHeader>
                                            <div className="mb-2 flex items-start justify-between">
                                                <Badge
                                                    variant="secondary"
                                                    className={statusConfig[solution.status]?.color || 'bg-gray-500/10'}
                                                >
                                                    <StatusIcon className="mr-1 h-3 w-3" />
                                                    {statusConfig[solution.status]?.label || solution.status}
                                                </Badge>
                                            </div>
                                            <CardTitle className="line-clamp-2">
                                                {solution.title}
                                            </CardTitle>
                                            <CardDescription className="line-clamp-3">
                                                {solution.description || 'No description available'}
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                                    {solution.requirements && (
                                                        <div className="flex items-center gap-1">
                                                            <FileText className="h-4 w-4" />
                                                            <span>Requirements</span>
                                                        </div>
                                                    )}
                                                    {solution.technical_solution && (
                                                        <div className="flex items-center gap-1">
                                                            <Code className="h-4 w-4" />
                                                            <span>Solution</span>
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="text-xs text-muted-foreground">
                                                    Updated {formatDate(solution.updated_at)}
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </Link>
                            );
                        })}
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
