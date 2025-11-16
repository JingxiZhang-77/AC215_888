'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, hasRole, getUserData } from '@/lib/Common';
import DataService from '@/lib/DataService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

export default function ClassifyPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [description, setDescription] = useState('');
  const [department, setDepartment] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const departments = [
    { value: 'internal_medicine', label: 'Internal Medicine' },
    { value: 'surgery', label: 'Surgery' },
    { value: 'ob_gyn_nicu', label: 'OB/GYN/NICU' },
    { value: 'radiology_imaging', label: 'Radiology/Imaging' },
    { value: 'outpatient_er', label: 'Outpatient/ER' },
  ];

  useEffect(() => {
    if (!isAuthenticated() || !hasRole(['admin', 'doctor', 'nurse'])) {
      router.push('/');
      return;
    }
    const userData = getUserData();
    setUser(userData);
    setDepartment(userData.department || '');
  }, [router]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);

    try {
      const response = await DataService.Classification.classifySingle(description, department);
      setResult(response);
    } catch (err) {
      console.error('Classification error:', err);
      setError(err.response?.data?.detail || 'Classification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setDescription('');
    setResult(null);
    setError('');
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Single Incident Classification</h1>
        <p className="text-muted-foreground mt-2">
          Classify individual safety incidents with AI-powered analysis
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Incident Details</CardTitle>
          <CardDescription>
            Provide the incident description and department for classification
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="department">Department *</Label>
              <Select
                value={department}
                onValueChange={setDepartment}
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  {departments.map((dept) => (
                    <SelectItem key={dept.value} value={dept.value}>
                      {dept.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Incident Description *</Label>
              <Textarea
                id="description"
                placeholder="Enter the safety incident description in detail..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                disabled={loading}
                rows={8}
                className="resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Provide as much detail as possible for accurate classification
              </p>
            </div>

            <div className="flex gap-3">
              <Button type="submit" disabled={loading || !description.trim() || !department}>
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Classifying...
                  </>
                ) : (
                  'Classify Incident'
                )}
              </Button>
              {(description || result) && (
                <Button type="button" variant="outline" onClick={handleReset}>
                  Reset
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <CardTitle>Classification Result</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Classification Code */}
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">Classification:</span>
              <span className={`classification-code code-${result.classification_code}`}>
                {result.classification_code}
              </span>
            </div>

            {/* Department */}
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">Department:</span>
              <span className="font-medium">
                {departments.find(d => d.value === result.department)?.label || result.department}
              </span>
            </div>

            {/* Rationales */}
            <div className="space-y-3 mt-4">
              <h4 className="font-semibold text-sm">Classification Rationales:</h4>
              
              <div className="rationale-section">
                <h5 className="font-medium text-sm mb-2">1. Deviation from GAPS</h5>
                <p className="text-sm">{result.deviation_rationale}</p>
              </div>

              <div className="rationale-section">
                <h5 className="font-medium text-sm mb-2">2. Patient Reach</h5>
                <p className="text-sm">{result.reach_rationale}</p>
              </div>

              <div className="rationale-section">
                <h5 className="font-medium text-sm mb-2">3. Harm Assessment</h5>
                <p className="text-sm">{result.harm_rationale}</p>
              </div>
            </div>

            {/* Processing Time */}
            {result.processing_time && (
              <div className="text-xs text-muted-foreground pt-2 border-t">
                Processed in {result.processing_time.toFixed(2)}s
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
