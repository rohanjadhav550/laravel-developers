import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import BackButton from '@/components/back-button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link, router } from '@inertiajs/react';
import { CheckCircle, Clock, Code, FileText, Lightbulb, XCircle, Calendar } from 'lucide-react';

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
    conversation?: any;
    project?: any;
    user?: any;
}

interface SolutionShowProps {
    solution: Solution;
    project: Project;
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

export default function SolutionShow({ solution, project }: SolutionShowProps) {
    const breadcrumbs: BreadcrumbItem[] = [
        {
            title: project?.name || 'Project',
            href: `/projects/${project?.slug || 'unknown'}/home`,
        },
        {
            title: 'Solutions',
            href: `/projects/${project?.slug || 'unknown'}/solutions`,
        },
        {
            title: solution.title,
            href: `/projects/${project?.slug || 'unknown'}/solutions/${solution.id}`,
        },
    ];

    const StatusIcon = statusConfig[solution.status]?.icon || FileText;

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString(undefined, {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const handleApproveRequirements = () => {
        router.post(`/projects/${project?.slug || 'unknown'}/solutions/${solution.id}/approve-requirements`, {}, {
            preserveScroll: true,
        });
    };

    const handleApproveSolution = () => {
        router.post(`/projects/${project?.slug || 'unknown'}/solutions/${solution.id}/approve-solution`, {}, {
            preserveScroll: true,
        });
    };

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={`${solution.title} - Solutions`} />
            <div className="flex h-full flex-1 flex-col gap-6 p-4">
                <div className="mb-2">
                    <BackButton label="Back to Solutions" />
                </div>

                {/* Header */}
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="mb-2 flex items-center gap-2">
                            <Badge
                                variant="secondary"
                                className={statusConfig[solution.status]?.color || 'bg-gray-500/10'}
                            >
                                <StatusIcon className="mr-1 h-3 w-3" />
                                {statusConfig[solution.status]?.label || solution.status}
                            </Badge>
                        </div>
                        <h1 className="text-3xl font-bold">{solution.title}</h1>
                        {solution.description && (
                            <p className="mt-2 text-muted-foreground">{solution.description}</p>
                        )}
                    </div>
                    <div className="flex gap-2">
                        {solution.status === 'requirement_ready' && !solution.requirement_approved_at && (
                            <Button onClick={handleApproveRequirements}>
                                <CheckCircle className="mr-2 h-4 w-4" />
                                Approve Requirements
                            </Button>
                        )}
                        {solution.status === 'solution_ready' && !solution.solution_approved_at && (
                            <Button onClick={handleApproveSolution}>
                                <CheckCircle className="mr-2 h-4 w-4" />
                                Approve Solution
                            </Button>
                        )}
                        <Button asChild variant="outline">
                            <Link href={`/projects/${project?.slug || 'unknown'}/chat`}>
                                Continue Chat
                            </Link>
                        </Button>
                    </div>
                </div>

                {/* Metadata */}
                <Card>
                    <CardContent className="pt-6">
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                            <div className="flex items-center gap-2">
                                <Calendar className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <p className="text-sm text-muted-foreground">Created</p>
                                    <p className="text-sm font-medium">{formatDate(solution.created_at)}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <Calendar className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <p className="text-sm text-muted-foreground">Updated</p>
                                    <p className="text-sm font-medium">{formatDate(solution.updated_at)}</p>
                                </div>
                            </div>
                            {solution.requirement_approved_at && (
                                <div className="flex items-center gap-2">
                                    <CheckCircle className="h-4 w-4 text-green-600" />
                                    <div>
                                        <p className="text-sm text-muted-foreground">Requirements Approved</p>
                                        <p className="text-sm font-medium">{formatDate(solution.requirement_approved_at)}</p>
                                    </div>
                                </div>
                            )}
                            {solution.solution_approved_at && (
                                <div className="flex items-center gap-2">
                                    <CheckCircle className="h-4 w-4 text-green-600" />
                                    <div>
                                        <p className="text-sm text-muted-foreground">Solution Approved</p>
                                        <p className="text-sm font-medium">{formatDate(solution.solution_approved_at)}</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Requirements */}
                {solution.requirements && (
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="h-5 w-5" />
                                Requirements
                            </CardTitle>
                            <CardDescription>
                                Gathered requirements for this solution
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                                {solution.requirements}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Technical Solution */}
                {solution.technical_solution && (
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Code className="h-5 w-5" />
                                Technical Solution
                            </CardTitle>
                            <CardDescription>
                                Proposed technical implementation
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                                {solution.technical_solution}
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* No Content State */}
                {!solution.requirements && !solution.technical_solution && (
                    <Card className="flex flex-col items-center justify-center p-12">
                        <Lightbulb className="mb-4 h-12 w-12 text-muted-foreground" />
                        <h3 className="mb-2 text-lg font-semibold">No details yet</h3>
                        <p className="mb-4 text-center text-muted-foreground">
                            Requirements and solutions will appear here as they are gathered through conversation.
                        </p>
                        <Button asChild>
                            <Link href={`/projects/${project?.slug || 'unknown'}/chat`}>
                                Continue Chat
                            </Link>
                        </Button>
                    </Card>
                )}
            </div>
        </AppLayout>
    );
}
