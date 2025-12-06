import AppLayout from '@/layouts/app-layout';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Head, Link, router, useForm } from '@inertiajs/react';
import { ArrowLeft, FileText, Upload, RefreshCw, Trash2, Database, Search } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

interface Document {
    id: number;
    title: string;
    status: 'pending' | 'vectorized' | 'failed';
    created_at: string;
    updated_at: string;
}

interface KnowledgeBase {
    id: number;
    name: string;
    description: string;
    agent_type: string;
    status: string;
    document_count: number;
    vector_count: number;
}

interface PageProps {
    kb: KnowledgeBase;
    documents: {
        items: Document[];
        total: number;
    };
    stats: any;
}

export default function KnowledgeShow({ kb, documents, stats }: PageProps) {
    const [uploading, setUploading] = useState(false);
    const { data, setData, post, processing, errors, reset } = useForm({
        title: '',
        file: null as File | null,
    });

    const handleUpload = (e: React.FormEvent) => {
        e.preventDefault();
        if (!data.file) {
            toast.error('Please select a file');
            return;
        }

        post(`/admin/knowledge-bases/${kb.id}/upload`, {
            onSuccess: () => {
                toast.success('Document uploaded successfully');
                reset();
                // Switch to documents tab if possible or just rely on router reload
            },
            onError: () => {
                toast.error('Failed to upload document');
            }
        });
    };

    const handleDelete = (docId: number) => {
        if (confirm('Are you sure you want to delete this document?')) {
            router.delete(`/admin/knowledge-bases/${kb.id}/documents/${docId}`, {
                onSuccess: () => toast.success('Document deleted'),
                onError: () => toast.error('Failed to delete document'),
            });
        }
    };

    const handleVectorize = () => {
        router.post(`/admin/knowledge-bases/${kb.id}/vectorize`, {}, {
            preserveScroll: true,
            onSuccess: (page) => {
                toast.success('Vectorization completed successfully!');
                // Reload the page to show updated document statuses
                router.reload({ only: ['documents', 'kb', 'stats'] });
            },
            onError: (errors) => {
                console.error('Vectorization error:', errors);
                const errorMessage = typeof errors === 'object' ? JSON.stringify(errors) : errors;
                toast.error(`Vectorization failed: ${errorMessage}`);
            },
        });
    };

    return (
        <AppLayout breadcrumbs={[
            { title: 'Knowledge Bases', href: '/admin/knowledge-bases' },
            { title: kb.name }
        ]}>
            <Head title={`${kb.name} - Knowledge Base`} />

            <div className="flex h-full flex-1 flex-col gap-6 p-6">
                <div className="mb-2">
                    <Button variant="ghost" size="sm" asChild>
                        <Link href="/admin/knowledge-bases">
                            <ArrowLeft className="mr-2 h-4 w-4" /> Back
                        </Link>
                    </Button>
                </div>

                {/* Header */}
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
                            {kb.name}
                            <Badge variant={kb.status === 'active' ? 'default' : 'secondary'}>
                                {kb.status}
                            </Badge>
                        </h1>
                        <p className="text-muted-foreground mt-1">{kb.description}</p>
                        <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                                <FileText className="h-4 w-4" /> {stats?.document_count || kb.document_count} Documents
                            </span>
                            <span className="flex items-center gap-1">
                                <Database className="h-4 w-4" /> {stats?.vector_count || kb.vector_count} Vectors
                            </span>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button onClick={handleVectorize} variant="outline">
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Re-Vectorize
                        </Button>
                    </div>
                </div>

                <Tabs defaultValue="documents" className="w-full">
                    <TabsList>
                        <TabsTrigger value="documents">Documents</TabsTrigger>
                        <TabsTrigger value="upload">Upload</TabsTrigger>
                        <TabsTrigger value="settings">Settings</TabsTrigger>
                    </TabsList>

                    <TabsContent value="documents" className="mt-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Documents</CardTitle>
                                <CardDescription>Manage documents in this knowledge base.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Title</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Added</TableHead>
                                            <TableHead className="text-right">Actions</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {documents.items.length === 0 ? (
                                            <TableRow>
                                                <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                                                    No documents found. Upload one to get started.
                                                </TableCell>
                                            </TableRow>
                                        ) : (
                                            documents.items.map((doc) => (
                                                <TableRow key={doc.id}>
                                                    <TableCell className="font-medium">
                                                        <div className="flex items-center gap-2">
                                                            <FileText className="h-4 w-4 text-muted-foreground" />
                                                            {doc.title}
                                                        </div>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Badge variant="outline" className={
                                                            doc.status === 'vectorized' ? 'border-green-500 text-green-500' :
                                                                doc.status === 'failed' ? 'border-red-500 text-red-500' : ''
                                                        }>
                                                            {doc.status}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                                                    <TableCell className="text-right">
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            className="text-red-500 hover:text-red-700 hover:bg-red-50"
                                                            onClick={() => handleDelete(doc.id)}
                                                        >
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="upload" className="mt-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Upload Document</CardTitle>
                                <CardDescription>Upload text files (TXT, MD) or PDFs to add knowledge.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleUpload} className="space-y-4 max-w-md">
                                    <div className="space-y-2">
                                        <Label htmlFor="title">Document Title (Optional)</Label>
                                        <Input
                                            id="title"
                                            placeholder="e.g. Project Architecture Guide"
                                            value={data.title}
                                            onChange={e => setData('title', e.target.value)}
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="file">File</Label>
                                        <div className="border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center gap-2 hover:bg-muted/50 transition-colors cursor-pointer relative">
                                            <Upload className="h-8 w-8 text-muted-foreground" />
                                            <p className="text-sm text-muted-foreground">Click to select or drag and drop</p>
                                            <span className="text-xs text-muted-foreground">TXT, MD, PDF up to 10MB</span>
                                            <Input
                                                id="file"
                                                type="file"
                                                className="absolute inset-0 opacity-0 cursor-pointer"
                                                onChange={e => setData('file', e.target.files ? e.target.files[0] : null)}
                                            />
                                        </div>
                                        {data.file && (
                                            <div className="text-sm font-medium flex items-center gap-2 text-primary">
                                                <FileText className="h-4 w-4" />
                                                {data.file.name}
                                            </div>
                                        )}
                                        {errors.file && <p className="text-sm text-red-500">{errors.file}</p>}
                                    </div>

                                    <Button type="submit" disabled={processing || !data.file}>
                                        {processing ? 'Uploading...' : 'Upload Document'}
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="settings" className="mt-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Settings</CardTitle>
                                <CardDescription>Configuration for this knowledge base.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="text-sm text-muted-foreground">
                                    Settings (chunk size, overlap, model) are configured in the `kb-admin` microservice configuration.
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </AppLayout>
    );
}
