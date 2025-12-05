import { NavFooter } from '@/components/nav-footer';
import { NavMain } from '@/components/nav-main';
import { NavUser } from '@/components/nav-user';
import { ProjectSwitcher } from '@/components/project-switcher';
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarGroup,
    SidebarGroupLabel,
} from '@/components/ui/sidebar';
import { type NavItem, type SharedData } from '@/types';
import { Link, usePage } from '@inertiajs/react';
import { BookOpen, Folder, Home, LayoutGrid, BrainCircuit, Database } from 'lucide-react';
import AppLogo from './app-logo';

const footerNavItems: NavItem[] = [
    {
        title: 'Repository',
        href: 'https://github.com/laravel/react-starter-kit',
        icon: Folder,
    },
    {
        title: 'Documentation',
        href: 'https://laravel.com/docs/starter-kits#react',
        icon: BookOpen,
    },
];

export function AppSidebar() {
    const { currentProject } = usePage<SharedData>().props;

    const mainNavItems: NavItem[] = currentProject
        ? [
            {
                title: 'Home',
                href: `/projects/${currentProject.slug}/home`,
                icon: Home,
            },
            {
                title: 'Dashboard',
                href: `/projects/${currentProject.slug}/dashboard`,
                icon: LayoutGrid,
            },
        ]
        : [
            {
                title: 'Projects',
                href: '/projects',
                icon: Folder,
            },
        ];

    return (
        <Sidebar collapsible="icon" variant="inset">
            <SidebarHeader>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton size="lg" asChild>
                            <Link href="/projects" prefetch>
                                <AppLogo />
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
                {currentProject && <ProjectSwitcher />}
            </SidebarHeader>

            <SidebarContent>
                <NavMain items={mainNavItems} />

                <SidebarGroup className="px-2 py-0">
                    <SidebarGroupLabel>Admin</SidebarGroupLabel>
                    <SidebarMenu>
                        <SidebarMenuItem>
                            <SidebarMenuButton asChild isActive={usePage().url.startsWith('/admin/learned-knowledge')}>
                                <Link href={route('admin.learned-knowledge.index')}>
                                    <BrainCircuit />
                                    <span>Review Knowledge</span>
                                </Link>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                        <SidebarMenuItem>
                            <SidebarMenuButton asChild isActive={usePage().url.startsWith('/admin/knowledge-bases')}>
                                <Link href={route('admin.knowledge.index')}>
                                    <Database />
                                    <span>Knowledge Bases</span>
                                </Link>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </SidebarGroup>
            </SidebarContent>


            <SidebarFooter>
                <NavFooter items={footerNavItems} className="mt-auto" />
                <NavUser />
            </SidebarFooter>
        </Sidebar>
    );
}
