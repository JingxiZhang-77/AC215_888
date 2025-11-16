'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, hasRole, getUserData } from '@/lib/Common';
import DataService from '@/lib/DataService';
import { DEPARTMENTS, departmentApiToSlug } from '@/lib/departments';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, CheckCircle2, Loader2, Mic, FileAudio } from 'lucide-react';

export default function AudioPage() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [language, setLanguage] = useState('en-US');
  const [department, setDepartment] = useState('');
  const [autoTranslate, setAutoTranslate] = useState(true);
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [transcriptionResult, setTranscriptionResult] = useState(null);
  const [classificationResult, setClassificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('transcribe');

  useEffect(() => {
    if (!isAuthenticated() || !hasRole(['admin', 'doctor', 'nurse'])) {
      router.push('/');
      return;
    }
    const userData = getUserData();
    setUser(userData);
    const preferredDepartment = departmentApiToSlug(userData?.department) || userData?.department || '';
    setDepartment(preferredDepartment);
    fetchSupportedLanguages();
  }, [router]);

  const fetchSupportedLanguages = async () => {
    try {
      const response = await DataService.Audio.getSupportedLanguages();
      setSupportedLanguages(response.languages);
    } catch (err) {
      console.error('Failed to fetch languages:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setError('');
    setTranscriptionResult(null);
    setClassificationResult(null);

    if (selectedFile) {
      // Validate file type
      const validTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/ogg', 'audio/flac'];
      if (!validTypes.some(type => selectedFile.type.includes(type.split('/')[1]))) {
        setError('Please select a valid audio file (WAV, MP3, OGG, FLAC)');
        setAudioFile(null);
        e.target.value = '';
        return;
      }

      setAudioFile(selectedFile);
    }
  };

  const handleTranscribe = async (e) => {
    e.preventDefault();
    if (!audioFile) return;

    setError('');
    setTranscriptionResult(null);
    setLoading(true);

    try {
      const response = await DataService.Audio.transcribe(audioFile, language, autoTranslate);
      setTranscriptionResult(response);
    } catch (err) {
      console.error('Transcription error:', err);
      setError(err.response?.data?.detail || 'Transcription failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClassify = async (e) => {
    e.preventDefault();
    if (!audioFile || !department) return;

    setError('');
    setTranscriptionResult(null);
    setClassificationResult(null);
    setLoading(true);

    try {
      const response = await DataService.Classification.classifyAudio(
        audioFile,
        language,
        department,
        autoTranslate
      );
      setTranscriptionResult(response.transcription);
      setClassificationResult(response.classification);
    } catch (err) {
      console.error('Audio classification error:', err);
      setError(err.response?.data?.detail || 'Audio classification failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setAudioFile(null);
    setTranscriptionResult(null);
    setClassificationResult(null);
    setError('');
    const fileInput = document.getElementById('audio-upload');
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
        <h1 className="text-3xl font-bold">Audio Transcription & Classification</h1>
        <p className="text-muted-foreground mt-2">
          Transcribe and classify incidents from audio recordings
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="transcribe">Transcribe Only</TabsTrigger>
          <TabsTrigger value="classify">Transcribe & Classify</TabsTrigger>
        </TabsList>

        {/* Transcribe Only Tab */}
        <TabsContent value="transcribe" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="w-5 h-5" />
                Audio Transcription
              </CardTitle>
              <CardDescription>
                Convert audio recordings to text in 5 supported languages
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleTranscribe} className="space-y-4">
                {error && (
                  <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="audio-upload">Audio File *</Label>
                  <Input
                    id="audio-upload"
                    type="file"
                    accept="audio/*"
                    onChange={handleFileChange}
                    disabled={loading}
                    className="cursor-pointer"
                  />
                  {audioFile && (
                    <p className="text-sm text-muted-foreground">
                      Selected: {audioFile.name}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="language">Language *</Label>
                  <Select value={language} onValueChange={setLanguage} disabled={loading}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {supportedLanguages.map((lang) => (
                        <SelectItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="auto-translate"
                    checked={autoTranslate}
                    onChange={(e) => setAutoTranslate(e.target.checked)}
                    disabled={loading}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="auto-translate" className="cursor-pointer">
                    Auto-translate to English (if non-English)
                  </Label>
                </div>

                <div className="flex gap-3">
                  <Button type="submit" disabled={loading || !audioFile}>
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Transcribing...
                      </>
                    ) : (
                      <>
                        <FileAudio className="w-4 h-4 mr-2" />
                        Transcribe Audio
                      </>
                    )}
                  </Button>
                  {(audioFile || transcriptionResult) && (
                    <Button type="button" variant="outline" onClick={handleReset}>
                      Reset
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Transcribe & Classify Tab */}
        <TabsContent value="classify" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="w-5 h-5" />
                Audio Classification
              </CardTitle>
              <CardDescription>
                Transcribe audio and automatically classify the safety incident
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleClassify} className="space-y-4">
                {error && (
                  <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="audio-upload-classify">Audio File *</Label>
                  <Input
                    id="audio-upload-classify"
                    type="file"
                    accept="audio/*"
                    onChange={handleFileChange}
                    disabled={loading}
                    className="cursor-pointer"
                  />
                  {audioFile && (
                    <p className="text-sm text-muted-foreground">
                      Selected: {audioFile.name}
                    </p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="language-classify">Language *</Label>
                    <Select value={language} onValueChange={setLanguage} disabled={loading}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {supportedLanguages.map((lang) => (
                          <SelectItem key={lang.code} value={lang.code}>
                            {lang.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="department-classify">Department *</Label>
                    <Select value={department} onValueChange={setDepartment} disabled={loading}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select department" />
                      </SelectTrigger>
                      <SelectContent>
                        {DEPARTMENTS.map((dept) => (
                          <SelectItem key={dept.slug} value={dept.slug}>
                            {dept.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="auto-translate-classify"
                    checked={autoTranslate}
                    onChange={(e) => setAutoTranslate(e.target.checked)}
                    disabled={loading}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="auto-translate-classify" className="cursor-pointer">
                    Auto-translate to English for classification
                  </Label>
                </div>

                <div className="flex gap-3">
                  <Button type="submit" disabled={loading || !audioFile || !department}>
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      'Transcribe & Classify'
                    )}
                  </Button>
                  {(audioFile || classificationResult) && (
                    <Button type="button" variant="outline" onClick={handleReset}>
                      Reset
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Transcription Result */}
      {transcriptionResult && !classificationResult && (
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <CardTitle>Transcription Result</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-sm text-muted-foreground">Detected Language:</Label>
              <p className="font-medium">
                {supportedLanguages.find(l => l.code === transcriptionResult.language)?.name || transcriptionResult.language}
              </p>
            </div>

            {transcriptionResult.was_translated && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800">
                  ✓ Text was automatically translated to English
                </p>
              </div>
            )}

            <div>
              <Label className="text-sm text-muted-foreground">Transcribed Text:</Label>
              <div className="mt-2 p-4 bg-muted rounded-lg">
                <p className="text-sm whitespace-pre-wrap">{transcriptionResult.transcript}</p>
              </div>
            </div>

            {transcriptionResult.confidence && (
              <div className="text-xs text-muted-foreground pt-2 border-t">
                Confidence: {(transcriptionResult.confidence * 100).toFixed(1)}%
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Classification Result */}
      {classificationResult && transcriptionResult && (
        <>
          <Card className="border-2 border-primary/20">
            <CardHeader>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <CardTitle>Transcription</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm text-muted-foreground">Language:</Label>
                  <p className="font-medium">
                    {supportedLanguages.find(l => l.code === transcriptionResult.language)?.name}
                  </p>
                </div>
                {transcriptionResult.was_translated && (
                  <div className="p-2 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-800">
                    Translated to English
                  </div>
                )}
              </div>

              <div>
                <Label className="text-sm text-muted-foreground">Transcribed Text:</Label>
                <div className="mt-2 p-3 bg-muted rounded-lg">
                  <p className="text-sm">{transcriptionResult.transcript}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-2 border-primary/20">
            <CardHeader>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <CardTitle>Classification Result</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <span className="text-sm text-muted-foreground">Classification:</span>
                <div className="flex items-center gap-3">
                  <span className={`classification-code code-${classificationResult.classification_code}`}>
                    {classificationResult.classification_code}
                  </span>
                  <span className="text-sm font-medium">
                    {classificationResult.classification_label}
                  </span>
                </div>
              </div>

              {classificationResult.department_label && (
                <div className="flex items-center gap-4">
                  <span className="text-sm text-muted-foreground">Department:</span>
                  <span className="font-medium">
                    {classificationResult.department_label}
                  </span>
                </div>
              )}

              {classificationResult.classification_rationale && (
                <div className="p-3 bg-muted rounded-md text-sm">
                  {classificationResult.classification_rationale}
                </div>
              )}

              <div className="space-y-3 mt-4">
                <h4 className="font-semibold text-sm">Classification Rationales:</h4>
                
                <div className="rationale-section">
                  <h5 className="font-medium text-sm mb-2">1. Deviation from GAPS</h5>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">
                    Decision: {classificationResult.deviation_check}
                  </p>
                  <p className="text-sm">{classificationResult.deviation_rationale}</p>
                </div>

                <div className="rationale-section">
                  <h5 className="font-medium text-sm mb-2">2. Patient Reach</h5>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">
                    Decision: {classificationResult.patient_reach_check}
                  </p>
                  <p className="text-sm">{classificationResult.patient_reach_rationale}</p>
                </div>

                <div className="rationale-section">
                  <h5 className="font-medium text-sm mb-2">3. Harm Assessment</h5>
                  <p className="text-xs uppercase tracking-wide text-muted-foreground">
                    Decision: {classificationResult.harm_level_check}
                  </p>
                  <p className="text-sm">{classificationResult.harm_level_rationale}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
