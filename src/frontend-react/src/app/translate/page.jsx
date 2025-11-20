'use client';
import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { detectLanguage, needsTranslation, simpleTranslate, BASE_API_URL } from '@/lib/Common';
import { Loader2, Globe2, CheckCircle2 } from 'lucide-react';

export default function TranslatePage() {
  const [input, setInput] = useState('');
  const [lang, setLang] = useState('en');
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
      const resp = await fetch(`${BASE_API_URL.replace(/\/$/, '')}/classification/classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: translated.translated })
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

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Text Translation</h1>
        <p className="text-muted-foreground mt-2">
          Paste non-English incident text → translate to English → classify.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Input Text</CardTitle>
          <CardDescription>Supports zh/es/fr/ja/ko detection</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            rows={6}
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="输入 / Pegue / Collez / Paste incident description..."
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
            Detected language: <span className="font-medium">{lang}</span>{needsTranslation(lang) && ' (needs translation)'}
          </p>
        </CardContent>
      </Card>

      {translated && (
        <Card className="border-green-500/40">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <CardTitle>Translation Result</CardTitle>
            </div>
            <CardDescription>Source: {translated.source} | Translated: {translated.wasTranslated ? 'Yes' : 'No'}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm">
              <strong>Original:</strong>
              <div className="p-2 mt-1 rounded bg-muted whitespace-pre-wrap">{translated.original}</div>
            </div>
            <div className="text-sm">
              <strong>English:</strong>
              <div className="p-2 mt-1 rounded bg-muted whitespace-pre-wrap">{translated.translated}</div>
            </div>
            <Button onClick={handleClassify} disabled={classLoading}>
              {classLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Classify Translated Text
            </Button>
          </CardContent>
        </Card>
      )}

      {classResult && (
        <Card>
          <CardHeader>
            <CardTitle>Classification</CardTitle>
            <CardDescription>Backend response</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="text-xs overflow-x-auto">{JSON.stringify(classResult, null, 2)}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
