'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, hasRole, getUserData } from '@/lib/Common';
import DataService from '@/lib/DataService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { AlertCircle, CheckCircle2, Loader2, Download, Upload, FileSpreadsheet } from 'lucide-react';

export default function BatchPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated() || !hasRole(['admin', 'doctor', 'nurse'])) {
      router.push('/');
      return;
    }
    setUser(getUserData());
  }, [router]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setError('');
    setResult(null);

    if (selectedFile) {
      // Validate file type
      const validTypes = ['.csv', '.xlsx', '.xls'];
      const fileExtension = selectedFile.name.toLowerCase().slice(selectedFile.name.lastIndexOf('.'));
      
      if (!validTypes.includes(fileExtension)) {
        setError('Please select a CSV or Excel file (.csv, .xlsx, .xls)');
        setFile(null);
        e.target.value = '';
        return;
      }

      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setError('');
    setResult(null);
    setLoading(true);

    try {
      const response = await DataService.Classification.classifyBatch(file);
      setResult(response);
    } catch (err) {
      console.error('Batch classification error:', err);
      setError(err.response?.data?.detail || 'Batch classification failed. Please check your file format.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadResults = () => {
    if (!result || !result.results_file) return;

    // Create a download link
    const link = document.createElement('a');
    link.href = `data:text/csv;charset=utf-8,${encodeURIComponent(result.results_file)}`;
    link.download = result.output_filename || 'classification_results.csv';
    link.click();
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError('');
    // Reset file input
    const fileInput = document.getElementById('file-upload');
    if (fileInput) fileInput.value = '';
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
        <h1 className="text-3xl font-bold">Batch Classification</h1>
        <p className="text-muted-foreground mt-2">
          Upload CSV or Excel files for bulk incident classification
        </p>
      </div>

      {/* Instructions Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5" />
            File Format Requirements
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Your file must contain the following columns:
          </p>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li><strong>description</strong> - The safety incident description</li>
            <li>
              <strong>department</strong> - One of: internal medicine, surgery, ob/gyn/nicu,
              radiology/imaging, outpatient/ER (underscored formats are accepted)
            </li>
          </ul>
          <p className="text-sm text-muted-foreground mt-3">
            Supported file formats: CSV (.csv), Excel (.xlsx, .xls). Need a starting point?
            Download the template below.
          </p>
          <Button variant="outline" size="sm" className="mt-2" asChild>
            <a href="/batch-template.csv" download>
              <Download className="w-4 h-4 mr-2" />
              Download Template
            </a>
          </Button>
        </CardContent>
      </Card>

      {/* Upload Card */}
      <Card>
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
          <CardDescription>
            Select a CSV or Excel file containing incident descriptions
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
              <Label htmlFor="file-upload">Select File *</Label>
              <div className="flex items-center gap-3">
                <Input
                  id="file-upload"
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileChange}
                  disabled={loading}
                  className="cursor-pointer"
                />
                {file && (
                  <span className="text-sm text-muted-foreground">
                    {file.name}
                  </span>
                )}
              </div>
            </div>

            <div className="flex gap-3">
              <Button type="submit" disabled={loading || !file}>
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    Process File
                  </>
                )}
              </Button>
              {(file || result) && (
                <Button type="button" variant="outline" onClick={handleReset}>
                  Reset
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Results Card */}
      {result && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <CardTitle>Processing Complete</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold">{result.total_incidents}</div>
                <div className="text-sm text-muted-foreground">Total Incidents</div>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold">{result.successful}</div>
                <div className="text-sm text-muted-foreground">Successful</div>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold">{result.failed}</div>
                <div className="text-sm text-muted-foreground">Failed</div>
              </div>
              <div className="text-center p-4 bg-muted rounded-lg">
                <div className="text-2xl font-bold">{result.processing_time?.toFixed(1)}s</div>
                <div className="text-sm text-muted-foreground">Time</div>
              </div>
            </div>

            {/* Classification Breakdown */}
            {result.summary && (
              <div className="space-y-3 mt-4">
                <h4 className="font-semibold">Classification Breakdown</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(result.summary).map(([code, count]) => (
                    <div key={code} className="flex items-center gap-2 p-3 border rounded-lg">
                      <span className={`classification-code code-${code} text-sm`}>
                        {code}
                      </span>
                      <span className="font-semibold">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Download Button */}
            <div className="pt-4 border-t">
              <Button onClick={handleDownloadResults}>
                <Download className="w-4 h-4 mr-2" />
                Download Results
              </Button>
              <p className="text-xs text-muted-foreground mt-2">
                Results will be downloaded as: {result.output_filename}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
