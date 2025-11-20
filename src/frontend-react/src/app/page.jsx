'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getUserData } from '@/lib/Common';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Activity, FileText, Mic, Users, BarChart3, Languages } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check authentication status
    const checkAuth = async () => {
      if (!isAuthenticated()) {
        router.push('/login');
        return;
      }
      
      const userData = getUserData();
      setUser(userData);
      setIsChecking(false);
    };

    checkAuth();
  }, [router]);

  // Show loading only while checking auth
  if (isChecking || !user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Activity className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  const features = [
    {
      title: 'Single Incident Classification',
      description: 'Classify individual safety incidents with AI-powered analysis',
      icon: FileText,
      href: '/classify',
      roles: ['admin', 'doctor', 'nurse'],
    },
    {
      title: 'Batch Processing',
      description: 'Upload CSV/Excel files for bulk incident classification',
      icon: BarChart3,
      href: '/batch',
      roles: ['admin', 'doctor', 'nurse'],
    },
    {
      title: 'Audio Transcription',
      description: 'Transcribe and classify incidents from audio recordings',
      icon: Mic,
      href: '/audio',
      roles: ['admin', 'doctor', 'nurse'],
    },
    {
      title: 'User Management',
      description: 'Manage system users and permissions',
      icon: Users,
      href: '/users',
      roles: ['admin'],
    },
    {
      title: 'Text Translation',
      description: 'Translate non-English incident text to English before classification',
      icon: Languages,
      href: '/translate',
      roles: ['admin', 'doctor', 'nurse', 'viewer'],
    },
  ];

  const canAccess = (requiredRoles) => {
    return requiredRoles.includes(user.role);
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight">
          Safety Event Classification System
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          AI-powered healthcare safety incident analysis with transparent decision rationales
        </p>
        <div className="flex items-center justify-center gap-2 mt-4">
          <span className="text-sm text-muted-foreground">Logged in as:</span>
          <span className="font-semibold">{user?.username || 'User'}</span>
          {user?.role && (
            <span className={`role-badge role-${user.role}`}>
              {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
            </span>
          )}
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-12">
        {features.map((feature) => {
          const Icon = feature.icon;
          const hasAccess = canAccess(feature.roles);

          return (
            <Card 
              key={feature.title}
              className={hasAccess ? 'hover:shadow-lg transition-all cursor-pointer' : 'opacity-50'}
              onClick={() => hasAccess && router.push(feature.href)}
            >
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-primary" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
              <CardContent>
                {hasAccess ? (
                  <Button className="w-full">
                    Open
                  </Button>
                ) : (
                  <Button disabled className="w-full">
                    Access Denied
                  </Button>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quick Stats */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>System Overview</CardTitle>
          <CardDescription>AI-powered classification methodology</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">3</div>
              <div className="text-sm text-muted-foreground">Classification Steps</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">5</div>
              <div className="text-sm text-muted-foreground">Departments</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">5</div>
              <div className="text-sm text-muted-foreground">Languages</div>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">4</div>
              <div className="text-sm text-muted-foreground">Classification Codes</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Classification Codes Reference */}
      <Card>
        <CardHeader>
          <CardTitle>Classification Codes</CardTitle>
          <CardDescription>Understanding the four-level classification system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-4 p-4 border rounded-lg">
            <span className="classification-code code-NSE">NSE</span>
            <div>
              <h4 className="font-semibold">No Safety Event</h4>
              <p className="text-sm text-muted-foreground">
                No deviation from Generally Accepted Performance Standards (GAPS) detected
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4 p-4 border rounded-lg">
            <span className="classification-code code-NME">NME</span>
            <div>
              <h4 className="font-semibold">No Medical Event</h4>
              <p className="text-sm text-muted-foreground">
                Deviation occurred but did not reach the patient
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4 p-4 border rounded-lg">
            <span className="classification-code code-PSE">PSE</span>
            <div>
              <h4 className="font-semibold">Precursor Safety Event</h4>
              <p className="text-sm text-muted-foreground">
                Deviation reached the patient with no or minimal harm
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4 p-4 border rounded-lg">
            <span className="classification-code code-SSE">SSE</span>
            <div>
              <h4 className="font-semibold">Serious Safety Event</h4>
              <p className="text-sm text-muted-foreground">
                Deviation reached the patient and caused moderate/severe harm or death
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
