import { PlaceholderPattern } from '@/components/ui/placeholder-pattern';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link } from '@inertiajs/react';
import { FolderOpen, Users, MessageSquare, History, Lightbulb, ArrowRight } from 'lucide-react';

interface HomeProps {
    project: Project;
    membersCount: number;
}

export default function Home({ project, membersCount }: HomeProps) {
    const breadcrumbs: BreadcrumbItem[] = [
        {
            title: project.name,
            href: `/projects/${project.slug}/home`,
        },
    ];

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title={`${project.name} - Home`} />
            <div className="flex h-full flex-1 flex-col gap-4 p-4">
                <div className="mb-4">
                    <h1 className="text-2xl font-bold">{project.name}</h1>
                    <p className="text-muted-foreground">Project dashboard</p>
                </div>

                {/* Project Stats */}
                <div className="grid gap-4 md:grid-cols-3">
                    <div className="rounded-xl border bg-card p-6">
                        <div className="flex items-center gap-4">
                            <div className="rounded-full bg-primary/10 p-3">
                                <FolderOpen className="h-6 w-6 text-primary" />
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Project</p>
                                <p className="text-xl font-semibold">{project.name}</p>
                            </div>
                        </div>
                    </div>

                    <div className="rounded-xl border bg-card p-6">
                        <div className="flex items-center gap-4">
                            <div className="rounded-full bg-primary/10 p-3">
                                <Users className="h-6 w-6 text-primary" />
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Members</p>
                                <p className="text-xl font-semibold">{membersCount}</p>
                            </div>
                        </div>
                    </div>

                    <div className="relative aspect-video overflow-hidden rounded-xl border border-sidebar-border/70 dark:border-sidebar-border">
                        <PlaceholderPattern className="absolute inset-0 size-full stroke-neutral-900/20 dark:stroke-neutral-100/20" />
                    </div>
                </div>

                {/* Main Actions */}
                <div className="mt-6">
                    <h2 className="mb-4 text-xl font-semibold">What would you like to do?</h2>
                    <div className="grid gap-4 md:grid-cols-3">
                        {/* Tell me your Idea */}
                        <Link href={`/projects/${project.slug}/chat`}>
                            <Card className="group cursor-pointer transition-all hover:shadow-lg hover:border-primary/50">
                                <CardHeader>
                                    <div className="mb-3 flex items-center justify-between">
                                        <div className="rounded-full bg-gradient-to-r from-purple-500 to-blue-500 p-3">
                                            <MessageSquare className="h-6 w-6 text-white" />
                                        </div>
                                        <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
                                    </div>
                                    <CardTitle>Tell me your Idea</CardTitle>
                                    <CardDescription>
                                        Chat with AI to develop your ideas and get instant help with your project
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-sm text-primary">Start chatting →</div>
                                </CardContent>
                            </Card>
                        </Link>

                        {/* Previous Conversations */}
                        <Link href={`/projects/${project.slug}/conversations`}>
                            <Card className="group cursor-pointer transition-all hover:shadow-lg hover:border-primary/50">
                                <CardHeader>
                                    <div className="mb-3 flex items-center justify-between">
                                        <div className="rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 p-3">
                                            <History className="h-6 w-6 text-white" />
                                        </div>
                                        <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
                                    </div>
                                    <CardTitle>Previous Conversations</CardTitle>
                                    <CardDescription>
                                        Review and continue your past chat conversations and discussions
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-sm text-primary">View conversations →</div>
                                </CardContent>
                            </Card>
                        </Link>

                        {/* Solutions */}
                        <Link href={`/projects/${project.slug}/solutions`}>
                            <Card className="group cursor-pointer transition-all hover:shadow-lg hover:border-primary/50">
                                <CardHeader>
                                    <div className="mb-3 flex items-center justify-between">
                                        <div className="rounded-full bg-gradient-to-r from-green-500 to-emerald-500 p-3">
                                            <Lightbulb className="h-6 w-6 text-white" />
                                        </div>
                                        <ArrowRight className="h-5 w-5 text-muted-foreground transition-transform group-hover:translate-x-1" />
                                    </div>
                                    <CardTitle>Solutions</CardTitle>
                                    <CardDescription>
                                        Browse accepted solutions and implementations for your project
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-sm text-primary">View solutions →</div>
                                </CardContent>
                            </Card>
                        </Link>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
