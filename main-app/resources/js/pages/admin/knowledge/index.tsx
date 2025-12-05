import AppLayout from '@/layouts/app-layout';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Head, Link } from '@inertiajs/react';
import { BookOpen, BrainCircuit, ChevronRight, FileText, Layers, Activity } from 'lucide-react';
import { Progress } from '@/components/ui/progress';

interface KnowledgeBase {
    id: number;
    name: string;
    description: string;
    agent_type: string;
    status: 'active' | 'archived' | 'draft';
    document_count: number;
    vector_count: number;
    last_vectorized_at: string | null;
}

interface PageProps {
    knowledgeBases: KnowledgeBase[];
    pendingReviewsCount: number;
}

export default function KnowledgeIndex({ knowledgeBases, pendingReviewsCount }: PageProps) {
    return (
        <AppLayout breadcrumbs={[{ title: 'Knowledge Bases' }]}>
            <Head title="Knowledge Bases" />

            <div className="flex h-full flex-1 flex-col gap-6 p-6">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Knowledge Bases</h1>
                        <p className="text-muted-foreground mt-1">Manage agent knowledge and documents</p>
                    </div>
                    {pendingReviewsCount > 0 && (
                        <Button asChild variant="outline" className="gap-2 border-yellow-500/50 bg-yellow-500/10 text-yellow-700 hover:bg-yellow-500/20 dark:text-yellow-400">
                            <Link href={route('admin.learned-knowledge.index')}>
                                <BrainCircuit className="h-4 w-4" />
                                {pendingReviewsCount} Pending Reviews
                            </Link>
                        </Button>
                    )}
                </div>

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {knowledgeBases.map((kb) => (
                        <Link key={kb.id} href={route('admin.knowledge.show', kb.id)}>
                            <Card className="h-full transition-all hover:border-primary/50 hover:shadow-md cursor-pointer group">
                                <CardHeader className="pb-3">
                                    <div className="flex justify-between items-start">
                                        <div className="space-y-1">
                                            <CardTitle className="text-xl group-hover:text-primary transition-colors">
                                                {kb.name}
                                            </CardTitle>
                                            <CardDescription className="line-clamp-2">
                                                {kb.description}
                                            </CardDescription>
                                        </div>
                                        <Badge variant={kb.status === 'active' ? 'default' : 'secondary'}>
                                            {kb.status}
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                                        <div className="flex flex-col gap-1">
                                            <span className="text-xs text-muted-foreground flex items-center gap-1">
                                                <FileText className="h-3 w-3" /> Documents
                                            </span>
                                            <span className="text-xl font-semibold">{kb.document_count}</span>
                                        </div>
                                        <div className="flex flex-col gap-1">
                                            <span className="text-xs text-muted-foreground flex items-center gap-1">
                                                <Layers className="h-3 w-3" /> Vectors
                                            </span>
                                            <span className="text-xl font-semibold">{kb.vector_count}</span>
                                        </div>
                                    </div>

                                    <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
                                        <span className="flex items-center gap-1">
                                            <Activity className="h-3 w-3" />
                                            Agent: {kb.agent_type.replace('_', ' ')}
                                        </span>
                                        <ChevronRight className="h-4 w-4 opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0" />
                                    </div>
                                </CardContent>
                            </Card>
                        </Link>
                    ))}

                    {/* Placeholder for creating new KB if needed later */}
                    <Card className="h-full border-dashed flex flex-col items-center justify-center p-6 text-center text-muted-foreground hover:border-primary/50 hover:bg-muted/50 transition-all cursor-not-allowed opacity-60">
                        <BookOpen className="h-10 w-10 mb-3 opacity-50" />
                        <h3 className="font-semibold">Create New Knowledge Base</h3>
                        <p className="text-sm mt-1">Contact system administrator to provision new agent KBs.</p>
                    </Card>
                </div>
            </div>
        </AppLayout>
    );
}
