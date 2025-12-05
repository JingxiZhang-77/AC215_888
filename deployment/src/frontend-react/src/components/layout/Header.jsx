'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { isAuthenticated, getUserData, removeAuthToken } from '@/lib/Common';
import { Button } from '@/components/ui/button';
import { Activity, FileText, Mic, BarChart3, Users, LogOut } from 'lucide-react';

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (isAuthenticated()) {
      setUser(getUserData());
    }
  }, [pathname]);

  const handleLogout = () => {
    removeAuthToken();
    localStorage.removeItem('user');
    router.push('/login');
  };

  const navItems = [
    { label: 'Home', href: '/', icon: Activity },
    { label: 'Classify', href: '/classify', icon: FileText, roles: ['admin', 'doctor', 'nurse'] },
    { label: 'Batch', href: '/batch', icon: BarChart3, roles: ['admin', 'doctor', 'nurse'] },
    { label: 'Audio', href: '/audio', icon: Mic, roles: ['admin', 'doctor', 'nurse'] },
    { label: 'Users', href: '/users', icon: Users, roles: ['admin'] },
  ];

  const canAccess = (roles) => {
    if (!roles || !user) return true;
    return roles.includes(user.role);
  };

  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 font-bold text-xl">
            <Activity className="w-6 h-6 text-primary" />
            <span>Safety Event Classifier</span>
          </Link>

          {/* Navigation */}
          {user && (
            <nav className="flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const hasAccess = canAccess(item.roles);
                const isActive = pathname === item.href;

                if (!hasAccess) return null;

                return (
                  <Link key={item.href} href={item.href}>
                    <Button
                      variant={isActive ? 'default' : 'ghost'}
                      size="sm"
                      className="gap-2"
                    >
                      <Icon className="w-4 h-4" />
                      <span className="hidden md:inline">{item.label}</span>
                    </Button>
                  </Link>
                );
              })}

              {/* User Info & Logout */}
              <div className="ml-4 flex items-center gap-2">
                <span className="text-sm text-muted-foreground hidden md:inline">
                  {user.username}
                </span>
                <span className={`role-badge role-${user.role} hidden md:inline-flex`}>
                  {user.role}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden md:inline">Logout</span>
                </Button>
              </div>
            </nav>
          )}

          {/* Login Button for Guests */}
          {!user && (
            <Link href="/login">
              <Button>Login</Button>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
