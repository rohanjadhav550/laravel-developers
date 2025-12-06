import AppLayout from '@/layouts/app-layout';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Head, router } from '@inertiajs/react';
import { useState } from 'react';
import { Check, X } from 'lucide-react';
import { toast } from 'sonner';

interface LearnedKnowledge {
    id: number;
    agent_type: string;
    knowledge_type: string;
    question: string;
    answer: string;
    confidence_score: number;
    created_at: string;
}

interface PageProps {
    pendingKnowledge: LearnedKnowledge[];
}

export default function LearnedKnowledgeIndex({ pendingKnowledge }: PageProps) {
    const [processing, setProcessing] = useState(false);

    const handleReview = (id: number, status: 'approved' | 'rejected') => {
        setProcessing(true);
        router.post(`/admin/learned-knowledge/${id}/review`, { status }, {
            preserveScroll: true,
            onFinish: () => setProcessing(false),
            onSuccess: () => {
                toast.success(`Knowledge ${status} successfully`);
            },
            onError: () => {
                toast.error('Failed to review knowledge');
            }
        });
    };

    return (
        <AppLayout breadcrumbs={[{ title: 'Learned Knowledge Review' }]}>
            <Head title="Review Learned Knowledge" />

            <div className="flex h-full flex-1 flex-col gap-4 p-4">
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold">Pending Review</h1>
                    <Badge variant="outline">{pendingKnowledge.length} Items</Badge>
                </div>

                <div className="flex-1 overflow-y-auto">
                    {pendingKnowledge.length === 0 ? (
                        <Card>
                            <CardContent className="p-8 text-center text-muted-foreground">
                                No learned knowledge pending review.
                            </CardContent>
                        </Card>
                    ) : (
                        <div className="grid gap-4 max-w-4xl mx-auto">
                            {pendingKnowledge.map((item) => (
                                <Card key={item.id} className="overflow-hidden">
                                    <div className="border-l-4 border-l-blue-500">
                                        <CardHeader className="pb-2 bg-muted/20">
                                            <div className="flex justify-between items-start">
                                                <div className="space-y-1">
                                                    <CardTitle className="text-lg flex items-center gap-2">
                                                        {item.knowledge_type.replace('_', ' ').toUpperCase()}
                                                        <Badge variant="secondary" className="text-xs">
                                                            {Math.round(item.confidence_score * 100)}% Confidence
                                                        </Badge>
                                                    </CardTitle>
                                                    <p className="text-xs text-muted-foreground">
                                                        Agent: {item.agent_type}
                                                    </p>
                                                </div>
                                                <div className="text-xs text-muted-foreground">
                                                    {new Date(item.created_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                        </CardHeader>
                                        <CardContent className="pt-4">
                                            <div className="space-y-4">
                                                <div>
                                                    <h3 className="text-sm font-semibold mb-1 text-muted-foreground">Question / Pattern</h3>
                                                    <div className="text-sm bg-muted/50 p-3 rounded-md border border-border/50">
                                                        {item.question}
                                                    </div>
                                                </div>
                                                <div>
                                                    <h3 className="text-sm font-semibold mb-1 text-muted-foreground">Answer / Solution</h3>
                                                    <div className="text-sm bg-muted/50 p-3 rounded-md border border-border/50 max-h-60 overflow-y-auto whitespace-pre-wrap font-mono">
                                                        {item.answer}
                                                    </div>
                                                </div>
                                                <div className="flex justify-end gap-2 pt-2 border-t mt-4">
                                                    <Button
                                                        variant="destructive"
                                                        size="sm"
                                                        onClick={() => handleReview(item.id, 'rejected')}
                                                        disabled={processing}
                                                    >
                                                        <X className="w-4 h-4 mr-1" /> Reject
                                                    </Button>
                                                    <Button
                                                        variant="default" // default is usually black/primary
                                                        size="sm"
                                                        onClick={() => handleReview(item.id, 'approved')}
                                                        disabled={processing}
                                                    >
                                                        <Check className="w-4 h-4 mr-1" /> Approve
                                                    </Button>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </div>
                                </Card>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </AppLayout>
    );
}
