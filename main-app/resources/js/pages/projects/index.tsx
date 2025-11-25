import TextLink from '@/components/text-link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link, router } from '@inertiajs/react';
import { FolderPlus, Search, Users } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useDebouncedCallback } from 'use-debounce';

interface PaginatedProjects {
    data: Project[];
    current_page: number;
    last_page: number;
    per_page: number;
    total: number;
    from: number | null;
    to: number | null;
}

interface ProjectsIndexProps {
    projects: PaginatedProjects;
    filters: {
        search: string;
        per_page: number;
    };
}

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'Projects',
        href: '/projects',
    },
];

export default function ProjectsIndex({ projects, filters }: ProjectsIndexProps) {
    const [search, setSearch] = useState(filters.search);
    const [perPage, setPerPage] = useState(filters.per_page.toString());

    const debouncedSearch = useDebouncedCallback((value: string) => {
        router.get('/projects', { search: value, per_page: perPage }, {
            preserveState: true,
            preserveScroll: true,
        });
    }, 300);

    useEffect(() => {
        debouncedSearch(search);
    }, [search]);

    const handlePerPageChange = (value: string) => {
        setPerPage(value);
        router.get('/projects', { search, per_page: value }, {
            preserveState: true,
            preserveScroll: true,
        });
    };

    const goToPage = (page: number) => {
        router.get('/projects', { search, per_page: perPage, page }, {
            preserveState: true,
            preserveScroll: true,
        });
    };

    return (
        <AppLayout breadcrumbs={breadcrumbs}>
            <Head title="Projects" />
            <div className="flex h-full flex-1 flex-col gap-6 p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold">Your Projects</h1>
                        <p className="text-muted-foreground">
                            Select a project to continue or create a new one
                        </p>
                    </div>
                    <Button asChild>
                        <Link href="/projects/create">
                            <FolderPlus className="mr-2 h-4 w-4" />
                            New Project
                        </Link>
                    </Button>
                </div>

                <div className="flex items-end gap-4">
                    <div className="flex-1">
                        <Label htmlFor="search">Search projects</Label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                id="search"
                                type="text"
                                placeholder="Search by name or slug..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="pl-9"
                            />
                        </div>
                    </div>
                    <div className="w-32">
                        <Label htmlFor="per-page">Per page</Label>
                        <Select value={perPage} onValueChange={handlePerPageChange}>
                            <SelectTrigger id="per-page">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="10">10</SelectItem>
                                <SelectItem value="25">25</SelectItem>
                                <SelectItem value="50">50</SelectItem>
                                <SelectItem value="100">100</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                {projects.total === 0 ? (
                    <Card className="flex flex-col items-center justify-center p-12">
                        <FolderPlus className="mb-4 h-12 w-12 text-muted-foreground" />
                        <h3 className="mb-2 text-lg font-semibold">
                            {search ? 'No projects found' : 'No projects yet'}
                        </h3>
                        <p className="mb-4 text-center text-muted-foreground">
                            {search
                                ? 'Try adjusting your search'
                                : 'Create your first project to get started'}
                        </p>
                        {!search && (
                            <Button asChild>
                                <Link href="/projects/create">Create Project</Link>
                            </Button>
                        )}
                    </Card>
                ) : (
                    <>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                            {projects.data.map((project) => (
                                <Card
                                    key={project.id}
                                    className="transition-shadow hover:shadow-md"
                                >
                                    <CardHeader>
                                        <CardTitle className="flex items-center justify-between">
                                            <span>{project.name}</span>
                                            {project.pivot?.role === 'owner' && (
                                                <span className="rounded-full bg-primary/10 px-2 py-1 text-xs text-primary">
                                                    Owner
                                                </span>
                                            )}
                                        </CardTitle>
                                        <CardDescription>/{project.slug}</CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center text-sm text-muted-foreground">
                                                <Users className="mr-1 h-4 w-4" />
                                                {project.users_count}{' '}
                                                {project.users_count === 1 ? 'member' : 'members'}
                                            </div>
                                            <TextLink href={`/projects/${project.slug}/home`}>
                                                Open
                                            </TextLink>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        {projects.last_page > 1 && (
                            <div className="flex items-center justify-between border-t pt-4">
                                <div className="text-sm text-muted-foreground">
                                    Showing {projects.from} to {projects.to} of {projects.total} projects
                                </div>
                                <div className="flex gap-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => goToPage(projects.current_page - 1)}
                                        disabled={projects.current_page === 1}
                                    >
                                        Previous
                                    </Button>
                                    <div className="flex items-center gap-1">
                                        {Array.from({ length: projects.last_page }, (_, i) => i + 1)
                                            .filter((page) => {
                                                return (
                                                    page === 1 ||
                                                    page === projects.last_page ||
                                                    Math.abs(page - projects.current_page) <= 1
                                                );
                                            })
                                            .map((page, index, array) => {
                                                const showEllipsis = index > 0 && page - array[index - 1] > 1;
                                                return (
                                                    <div key={page} className="flex items-center">
                                                        {showEllipsis && (
                                                            <span className="px-2 text-muted-foreground">...</span>
                                                        )}
                                                        <Button
                                                            variant={page === projects.current_page ? 'default' : 'outline'}
                                                            size="sm"
                                                            onClick={() => goToPage(page)}
                                                        >
                                                            {page}
                                                        </Button>
                                                    </div>
                                                );
                                            })}
                                    </div>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => goToPage(projects.current_page + 1)}
                                        disabled={projects.current_page === projects.last_page}
                                    >
                                        Next
                                    </Button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </AppLayout>
    );
}
