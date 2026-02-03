import { Shield, LayoutDashboard, Activity, Settings, Lock } from 'lucide-react';
import Link from 'next/link';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border flex flex-col">
        <div className="p-6 flex items-center gap-2 border-b border-border/50">
          <div className="w-8 h-8 rounded bg-primary text-primary-foreground flex items-center justify-center">
            <Shield size={18} />
          </div>
          <span className="font-bold tracking-tight">SecureSentinel</span>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          <NavLink href="/" icon={<LayoutDashboard size={18} />}>Overview</NavLink>
          <NavLink href="/activity" icon={<Activity size={18} />}>Activity Insights</NavLink>
          <NavLink href="/privacy" icon={<Lock size={18} />}>Privacy Center</NavLink>
          <NavLink href="/settings" icon={<Settings size={18} />}>Controls</NavLink>
        </nav>

        <div className="p-4 border-t border-border/50">
           <div className="p-3 bg-secondary/50 rounded-lg">
             <div className="text-xs text-muted-foreground uppercase font-semibold mb-1">Status</div>
             <div className="flex items-center gap-2 text-sm text-emerald-500">
               <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
               System Active
             </div>
           </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="h-16 border-b border-border/50 flex items-center justify-between px-8 bg-background/50 backdrop-blur sticky top-0 z-10">
           <div className="text-sm text-muted-foreground">Console / Overview</div>
           <div className="flex items-center gap-4">
             <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-xs font-medium">
               U
             </div>
           </div>
        </header>
        <div className="p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}

function NavLink({ href, icon, children }: { href: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <Link href={href} className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors">
      {icon}
      {children}
    </Link>
  );
}
