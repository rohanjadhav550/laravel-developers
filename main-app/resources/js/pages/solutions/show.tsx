import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import BackButton from '@/components/back-button';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link, router } from '@inertiajs/react';
import { CheckCircle, Clock, Code, FileText, Lightbulb, XCircle, Calendar, Loader2, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';

interface Solution {
    id: number;
    conversation_id: number;
    user_id: number;
    project_id: number | null;
    title: string;
    description: string | null;
    requirements: string | null;
    technical_solution: string | null;
    status: 'draft' | 'in_progress' | 'requirement_ready' | 'solution_ready' | 'approved' | 'rejected' | 'completed' | 'generating_solution' | 'generation_failed';
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

interface GenerationProgress {
    status: 'idle' | 'starting' | 'analyzing' | 'generating' | 'saving' | 'completed' | 'failed';
    progress: number;
    message: string;
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
    generating_solution: {
        label: 'Generating Solution',
        color: 'bg-indigo-500/10 text-indigo-700 dark:text-indigo-400',
        icon: Loader2,
    },
    generation_failed: {
        label: 'Generation Failed',
        color: 'bg-red-500/10 text-red-700 dark:text-red-400',
        icon: AlertCircle,
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

export default function SolutionShow({ solution: initialSolution, project }: SolutionShowProps) {
    const [solution, setSolution] = useState(initialSolution);
    const [isPublishing, setIsPublishing] = useState(false);
    const [progress, setProgress] = useState<GenerationProgress | null>(null);
    const [pollInterval, setPollInterval] = useState<NodeJS.Timeout | null>(null);

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

    // Poll for progress updates
    const startPolling = () => {
        const interval = setInterval(async () => {
            try {
                const response = await axios.get(
                    `/projects/${project?.slug}/solutions/${solution.id}/progress`
                );
                const progressData = response.data as GenerationProgress;
                setProgress(progressData);

                // Stop polling if completed or failed
                if (progressData.status === 'completed') {
                    stopPolling();
                    setProgress(null);
                    setIsPublishing(false);
                    // Full page reload to show the technical solution
                    window.location.reload();
                } else if (progressData.status === 'failed') {
                    stopPolling();
                    setIsPublishing(false);
                    // Reload page to get updated solution status
                    router.reload({ only: ['solution'] });
                }
            } catch (error) {
                console.error('Error fetching progress:', error);
            }
        }, 2000); // Poll every 2 seconds

        setPollInterval(interval);
    };

    const stopPolling = () => {
        if (pollInterval) {
            clearInterval(pollInterval);
            setPollInterval(null);
        }
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => stopPolling();
    }, []);

    const handlePublish = async () => {
        try {
            setIsPublishing(true);
            const response = await axios.post(
                `/projects/${project?.slug}/solutions/${solution.id}/publish`
            );

            if (response.data.success) {
                setProgress({
                    status: 'starting',
                    progress: 0,
                    message: 'Initializing...'
                });
                startPolling();
            }
        } catch (error: any) {
            console.error('Error publishing solution:', error);
            alert(error.response?.data?.message || 'Failed to publish solution');
            setIsPublishing(false);
        }
    };

    const handleRepublish = async () => {
        if (!confirm('Are you sure you want to regenerate the technical solution? This will overwrite the existing solution.')) {
            return;
        }

        try {
            setIsPublishing(true);
            const response = await axios.post(
                `/projects/${project?.slug}/solutions/${solution.id}/republish`
            );

            if (response.data.success) {
                setProgress({
                    status: 'starting',
                    progress: 0,
                    message: 'Initializing regeneration...'
                });
                startPolling();
            }
        } catch (error: any) {
            console.error('Error republishing solution:', error);
            alert(error.response?.data?.message || 'Failed to republish solution');
            setIsPublishing(false);
        }
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

    const isGenerating = isPublishing || solution.status === 'generating_solution' || (progress && ['starting', 'analyzing', 'generating', 'saving'].includes(progress.status));
    const hasRequirements = !!solution.requirements;
    const hasSolution = !!solution.technical_solution;

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
                                {solution.status === 'generating_solution' && (
                                    <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                                )}
                                {solution.status !== 'generating_solution' && <StatusIcon className="mr-1 h-3 w-3" />}
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

                {/* Generation Progress Alert */}
                {isGenerating && progress && (
                    <Alert className="border-indigo-500/50 bg-indigo-500/10">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <AlertTitle>Generating Technical Solution</AlertTitle>
                        <AlertDescription className="mt-2 space-y-3">
                            <p className="text-sm">{progress.message}</p>
                            <div className="space-y-2">
                                <Progress value={progress.progress} className="h-2" />
                                <p className="text-xs text-muted-foreground">
                                    {progress.progress}% complete • This may take 2-5 minutes
                                </p>
                            </div>
                            <div className="flex items-start gap-2 rounded-md bg-background/50 p-3 text-xs">
                                <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-indigo-500" />
                                <div className="space-y-1">
                                    <p className="font-medium">Using Intelligent AI Model</p>
                                    <p className="text-muted-foreground">
                                        Our AI is performing deep analysis and generating a comprehensive
                                        50+ page A-Z implementation guide with complete code structures,
                                        database schemas, security measures, and deployment strategies.
                                    </p>
                                </div>
                            </div>
                        </AlertDescription>
                    </Alert>
                )}

                {/* Generation Failed Alert */}
                {solution.status === 'generation_failed' && (
                    <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertTitle>Generation Failed</AlertTitle>
                        <AlertDescription>
                            Failed to generate technical solution. Please try again or contact support if the issue persists.
                        </AlertDescription>
                    </Alert>
                )}

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
                {hasRequirements && (
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle className="flex items-center gap-2">
                                        <FileText className="h-5 w-5" />
                                        Requirements
                                    </CardTitle>
                                    <CardDescription>
                                        Gathered requirements for this solution
                                    </CardDescription>
                                </div>
                                {!hasSolution && !isGenerating && (
                                    <Button onClick={handlePublish} size="lg" disabled={isGenerating}>
                                        {isGenerating ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                Generating...
                                            </>
                                        ) : (
                                            <>
                                                <Sparkles className="mr-2 h-4 w-4" />
                                                Publish Technical Solution
                                            </>
                                        )}
                                    </Button>
                                )}
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="prose prose-sm dark:prose-invert max-w-none">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    rehypePlugins={[rehypeRaw, rehypeSanitize]}
                                >
                                    {solution.requirements}
                                </ReactMarkdown>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* Technical Solution */}
                {hasSolution && (
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle className="flex items-center gap-2">
                                        <Code className="h-5 w-5" />
                                        Technical Solution
                                    </CardTitle>
                                    <CardDescription>
                                        Comprehensive A-Z implementation guide
                                    </CardDescription>
                                </div>
                                <Button onClick={handleRepublish} variant="outline" disabled={isGenerating}>
                                    {isGenerating ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Regenerating...
                                        </>
                                    ) : (
                                        <>
                                            <RefreshCw className="mr-2 h-4 w-4" />
                                            Republish Solution
                                        </>
                                    )}
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="prose prose-sm dark:prose-invert max-w-none">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm]}
                                    rehypePlugins={[rehypeRaw, rehypeSanitize]}
                                >
                                    {solution.technical_solution}
                                </ReactMarkdown>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {/* No Content State */}
                {!hasRequirements && !hasSolution && (
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
