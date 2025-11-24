import TextLink from '@/components/text-link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import AppLayout from '@/layouts/app-layout';
import { type BreadcrumbItem, type Project } from '@/types';
import { Head, Link } from '@inertiajs/react';
import { FolderPlus, Users } from 'lucide-react';

interface ProjectsIndexProps {
    projects: Project[];
}

const breadcrumbs: BreadcrumbItem[] = [
    {
        title: 'Projects',
        href: '/projects',
    },
];

export default function ProjectsIndex({ projects }: ProjectsIndexProps) {
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

                {projects.length === 0 ? (
                    <Card className="flex flex-col items-center justify-center p-12">
                        <FolderPlus className="mb-4 h-12 w-12 text-muted-foreground" />
                        <h3 className="mb-2 text-lg font-semibold">No projects yet</h3>
                        <p className="mb-4 text-center text-muted-foreground">
                            Create your first project to get started
                        </p>
                        <Button asChild>
                            <Link href="/projects/create">Create Project</Link>
                        </Button>
                    </Card>
                ) : (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {projects.map((project) => (
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
                )}
            </div>
        </AppLayout>
    );
}
