'use client';
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { detectLanguage, needsTranslation, simpleTranslate, BASE_API_URL } from '@/lib/Common';
import { Loader2, Globe2, CheckCircle2, AlertTriangle, ShieldAlert, ShieldCheck, ShieldX, Building2 } from 'lucide-react';

const DEPARTMENTS = [
  { value: 'internal medicine', label: 'Internal Medicine' },
  { value: 'surgery', label: 'Surgery' },
  { value: 'ob/gyn/nicu', label: 'OB/GYN/NICU' },
  { value: 'radiology/imaging', label: 'Radiology/Imaging' },
  { value: 'outpatient/ER', label: 'Outpatient/ER' },
];

const CLASSIFICATION_STYLES = {
  SSE: { bg: 'bg-red-100 dark:bg-red-900/30', border: 'border-red-500', text: 'text-red-700 dark:text-red-400', icon: ShieldX, label: 'Serious Safety Event' },
  PSE: { bg: 'bg-orange-100 dark:bg-orange-900/30', border: 'border-orange-500', text: 'text-orange-700 dark:text-orange-400', icon: ShieldAlert, label: 'Precursor Safety Event' },
  NME: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', border: 'border-yellow-500', text: 'text-yellow-700 dark:text-yellow-400', icon: AlertTriangle, label: 'Near Miss Event' },
  NSE: { bg: 'bg-green-100 dark:bg-green-900/30', border: 'border-green-500', text: 'text-green-700 dark:text-green-400', icon: ShieldCheck, label: 'No Safety Event' },
};

export default function TranslatePage() {
  const [input, setInput] = useState('');
  const [lang, setLang] = useState('en');
  const [department, setDepartment] = useState('internal medicine');
  const [translated, setTranslated] = useState(null);
  const [classResult, setClassResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [classLoading, setClassLoading] = useState(false);

  const handleDetect = () => setLang(detectLanguage(input));

  const handleTranslate = async () => {
    setLoading(true);
    setTranslated(null);
    setClassResult(null);
    try {
      const res = await simpleTranslate(input);
      setTranslated(res);
      setLang(res.detected);
    } finally {
      setLoading(false);
    }
  };

  const handleClassify = async () => {
    if (!translated) return;
    setClassLoading(true);
    setClassResult(null);
    try {
      const token = localStorage.getItem('auth_token');
      const resp = await fetch(`${BASE_API_URL.replace(/\/$/, '')}/classify/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ description: translated.translated, department })
      });
      const data = await resp.json();
      setClassResult(data);
    } catch {
      setClassResult({ error: 'Classification failed' });
    } finally {
      setClassLoading(false);
    }
  };

  const showTranslateBtn = input.trim() && needsTranslation(lang);
  const classCode = classResult?.classification_code || classResult?.final_classification_code;
  const classStyle = CLASSIFICATION_STYLES[classCode] || CLASSIFICATION_STYLES.NSE;
  const ClassIcon = classStyle.icon;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Text Translation & Classification</h1>
        <p className="text-muted-foreground mt-2">
          Translate non-English incident reports → classify with department-specific policies.
        </p>
      </div>

      {/* Department Selection */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            <CardTitle>Select Department</CardTitle>
          </div>
          <CardDescription>Choose the department for policy-based classification (RAG)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {DEPARTMENTS.map((dept) => (
              <Button
                key={dept.value}
                variant={department === dept.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setDepartment(dept.value)}
              >
                {dept.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Input Text */}
      <Card>
        <CardHeader>
          <CardTitle>Input Text</CardTitle>
          <CardDescription>Supports Simplified Chinese, Traditional Chinese, Spanish, French</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            rows={6}
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="输入简体中文 / 輸入繁體中文 / Escriba en español / Écrivez en français / Paste incident description..."
          />
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleDetect} disabled={!input}>
              <Globe2 className="w-4 h-4 mr-2" /> Detect
            </Button>
            <Button onClick={handleTranslate} disabled={!input || loading} className={!showTranslateBtn ? 'opacity-70' : ''}>
              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Globe2 className="w-4 h-4 mr-2" />}
              {needsTranslation(lang) ? 'Translate to English' : 'Already English'}
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            Detected language: <span className="font-medium">{
              {'zh-CN': 'Simplified Chinese', 'zh-TW': 'Traditional Chinese', 'zh': 'Chinese', 'es': 'Spanish', 'fr': 'French', 'en': 'English'}[lang] || lang
            }</span>{needsTranslation(lang) && ' (needs translation)'}
          </p>
        </CardContent>
      </Card>

      {/* Translation Result */}
      {translated && (
        <Card className="border-green-500/40">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <CardTitle>Translation Result</CardTitle>
            </div>
            <CardDescription>Source: {translated.source} | Translated: {translated.wasTranslated ? 'Yes' : 'No'}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-sm">
              <strong>Original:</strong>
              <div className="p-2 mt-1 rounded bg-muted whitespace-pre-wrap">{translated.original}</div>
            </div>
            <div className="text-sm">
              <strong>English:</strong>
              <div className="p-2 mt-1 rounded bg-muted whitespace-pre-wrap">{translated.translated}</div>
            </div>
            <div className="pt-2 border-t">
              <p className="text-sm text-muted-foreground mb-3">
                Department: <span className="font-medium">{DEPARTMENTS.find(d => d.value === department)?.label}</span>
              </p>
              <Button onClick={handleClassify} disabled={classLoading}>
                {classLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Classify Translated Text
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Classification Result */}
      {classResult && !classResult.error && (
        <Card className={`${classStyle.border} border-2`}>
          <CardHeader className={classStyle.bg}>
            <div className="flex items-center gap-3">
              <ClassIcon className={`w-8 h-8 ${classStyle.text}`} />
              <div>
                <CardTitle className={classStyle.text}>
                  {classCode}: {classStyle.label}
                </CardTitle>
                <CardDescription>
                  Department: {classResult.department_label || classResult.department}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 pt-4">
            {/* Classification Summary */}
            <div className={`p-4 rounded-lg ${classStyle.bg}`}>
              <h4 className="font-semibold mb-2">Classification Rationale</h4>
              <p className="text-sm">{classResult.classification_rationale || classResult.final_rationale || 'N/A'}</p>
            </div>

            {/* Step-by-step Analysis */}
            <div className="grid gap-3">
              <h4 className="font-semibold">Analysis Steps</h4>
              
              {/* GAPS Deviation Check */}
              <div className="p-3 rounded border bg-muted/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm">1. GAPS Deviation Check</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    classResult.deviation_check === 'Yes' || classResult.gaps_deviation_check === 'Yes' 
                      ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400' 
                      : 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-400'
                  }`}>
                    {classResult.deviation_check || classResult.gaps_deviation_check || 'N/A'}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">{classResult.deviation_rationale || classResult.gaps_rationale || 'N/A'}</p>
              </div>

              {/* Reached Patient Check */}
              <div className="p-3 rounded border bg-muted/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm">2. Reached Patient Check</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    classResult.patient_reach_check === 'Yes' || classResult.reached_patient_check === 'Yes'
                      ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-400' 
                      : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400'
                  }`}>
                    {classResult.patient_reach_check || classResult.reached_patient_check || 'N/A'}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">{classResult.patient_reach_rationale || classResult.reached_patient_rationale || 'N/A'}</p>
              </div>

              {/* Harm Level Check */}
              <div className="p-3 rounded border bg-muted/50">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-sm">3. Harm Level Assessment</span>
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400">
                    {classResult.harm_level_check || 'N/A'}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">{classResult.harm_level_rationale || 'N/A'}</p>
              </div>
            </div>

            {/* Timestamp */}
            {classResult.timestamp && (
              <p className="text-xs text-muted-foreground text-right pt-2 border-t">
                Classified at: {new Date(classResult.timestamp).toLocaleString()}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {classResult?.error && (
        <Card className="border-red-500">
          <CardHeader>
            <CardTitle className="text-red-600">Classification Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{classResult.error}</p>
            {classResult.detail && <p className="text-sm text-muted-foreground mt-2">{classResult.detail}</p>}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
