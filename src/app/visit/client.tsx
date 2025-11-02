'use client';

import { useCallback, useEffect, useMemo, useRef, useState, useTransition } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Spinner } from '@/components/ui/spinner';
import { Skeleton } from '@/components/ui/skeleton';
import {
  AlertCircle,
  CheckCircle2,
  ClipboardList,
  Clock3,
  FileAudio,
  Eye,
  FileText,
  Server,
  Smartphone,
  Monitor,
  Cpu,
  Zap,
  MemoryStick,
  HardDrive,
  Gpu,
  Copy,
  Check,
  Play,
  BarChart3,
} from 'lucide-react';

type Status = 'idle' | 'processing' | 'completed' | 'error';

type SystemInfo = Record<string, unknown> | null;

type SoapNoteDurations = {
  transcription_seconds: number;
  generation_seconds: number;
  total_seconds: number;
  audio_duration_seconds: number;
};

type SoapNotePayload = {
  soap_note: string;
  transcript: string;
  durations: SoapNoteDurations;
  progress_log: string[];
  request_id?: string;
};

type SoapNoteActionResult =
  | { success: true; data: SoapNotePayload }
  | { success: false; error: string };

type SoapNoteGeneratorProps = {
  systemInfo: SystemInfo;
  generateSoapNoteAction: (formData: FormData, requestId?: string) => Promise<SoapNoteActionResult>;
};

const statusLabelMap: Record<Status, string> = {
  idle: 'Idle',
  processing: 'Processing',
  completed: 'Completed',
  error: 'Needs attention',
};

const statusVariantMap: Record<Status, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  idle: 'outline',
  processing: 'secondary',
  completed: 'default',
  error: 'destructive',
};

const statusIconMap: Record<Status, typeof Clock3 | typeof CheckCircle2 | typeof AlertCircle> = {
  idle: Clock3,
  processing: Clock3,
  completed: CheckCircle2,
  error: AlertCircle,
};

const SYSTEM_INFO_FIELDS: { key: string; label: string; icon: typeof Server }[] = [
  { key: 'hostname', label: 'Host', icon: Server },
  { key: 'device', label: 'Device', icon: Smartphone },
  { key: 'os', label: 'OS', icon: Monitor },
  { key: 'cpu_name', label: 'CPU', icon: Cpu },
  { key: 'cpu_cores', label: 'CPU Cores', icon: Zap },
  { key: 'cpu_threads', label: 'CPU Threads', icon: Zap },
  { key: 'total_memory', label: 'Memory', icon: MemoryStick },
  { key: 'gpu_name', label: 'GPU', icon: Gpu },
  { key: 'gpu_cores', label: 'GPU Cores', icon: HardDrive },
  { key: 'gpu_memory', label: 'GPU Memory', icon: HardDrive },
];

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');



function formatSeconds(value?: number) {
  if (value === undefined || Number.isNaN(value)) {
    return '--';
  }
  return formatTime(value);
}

function formatDuration(value?: number) {
  if (value === undefined || Number.isNaN(value)) {
    return '--';
  }
  return formatTime(value);
}

function formatTime(seconds: number): string {
  const totalSeconds = Math.round(seconds);

  if (totalSeconds < 60) {
    return `${totalSeconds}s`;
  }

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const remainingSeconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else {
    return `${minutes}m ${remainingSeconds}s`;
  }
}

function getProgressMessage(
  status?: string,
  progress?: number,
  chunkInfo?: { current: number; total: number; status: string; text?: string }
): string {
  // If we have chunk information, treat it as transcript generation
  if (chunkInfo && chunkInfo.current && chunkInfo.total) {
    return 'Generating transcript...';
  }

  switch (status) {
    case 'created':
      return 'Visit created successfully';
    case 'queued':
      return 'Audio uploaded successfully';
    case 'processing':
      return 'Generating transcript...';
    case 'analyzing_audio':
      return 'Generating transcript...';
    case 'extracting_text':
      return 'Generating transcript...';
    case 'generating_soap':
      return 'Generating SOAP note...';
    case 'finalizing':
      return 'Generating SOAP note...';
    case 'completed':
      return 'SOAP note generated successfully';
    default:
      return '';
  }
}

export default function VisitPageClient({
  systemInfo,
  generateSoapNoteAction,
}: SoapNoteGeneratorProps) {
  const [status, setStatus] = useState<Status>('idle');
  const [soapNote, setSoapNote] = useState('');
  const [transcript, setTranscript] = useState('');
  const [progressLog, setProgressLog] = useState<string[]>([]);
  const [durations, setDurations] = useState<SoapNoteDurations | null>(null);
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [selectedFileUrl, setSelectedFileUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [progress, setProgress] = useState(0);
  const [timerActive, setTimerActive] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [viewMode, setViewMode] = useState<'markdown' | 'raw'>('markdown');
  const [isCopied, setIsCopied] = useState(false);
  const [ellipsisFrame, setEllipsisFrame] = useState(0);

  const formRef = useRef<HTMLFormElement | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const hasCompletedRef = useRef(false);
  const progressLogEndRef = useRef<HTMLDivElement | null>(null);

  const closeEventSource = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const fetchCompletedVisitData = useCallback(async (visitId?: string) => {
    if (!visitId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/soap/${visitId}`, {
        cache: 'no-store',
      });

      if (response.ok) {
        const data = await response.json() as {
          soap_note?: string;
          transcript?: string;
          generation_time?: number;
          audio_duration?: number;
          transcription_time?: number;
          soap_status?: string;
        };

        if (data.transcript) {
          setTranscript(data.transcript);
        }

        // Set all duration information if available
        if (data.audio_duration !== undefined || data.transcription_time !== undefined || data.generation_time !== undefined) {
          const audioDuration = data.audio_duration || 0;
          const transcriptionTime = data.transcription_time || 0;
          const generationTime = data.generation_time || 0;
          const totalTime = transcriptionTime + generationTime;

          setDurations({
            audio_duration_seconds: audioDuration,
            transcription_seconds: transcriptionTime,
            generation_seconds: generationTime,
            total_seconds: totalTime,
          });
        }
      }
    } catch (error) {
      console.error('Failed to fetch completed visit data:', error);
    }
  }, []);

  useEffect(() => {
    if (!timerActive || startTimeRef.current === null) {
      return;
    }

    const interval = window.setInterval(() => {
      if (startTimeRef.current !== null) {
        const diff = (performance.now() - startTimeRef.current) / 1000;
        setElapsed(diff);
      }
    }, 200);

    return () => window.clearInterval(interval);
  }, [timerActive]);

  useEffect(() => {
    return () => {
      closeEventSource();
      // Clean up object URL when component unmounts
      if (selectedFileUrl) {
        URL.revokeObjectURL(selectedFileUrl);
      }
    };
  }, [closeEventSource, selectedFileUrl]);

  // Animate ellipsis for progress messages
  useEffect(() => {
    if (status === 'processing') {
      const interval = setInterval(() => {
        setEllipsisFrame((prev) => (prev + 1) % 3);
      }, 500);
      return () => clearInterval(interval);
    }
  }, [status]);

  // Auto-scroll progress log to bottom when new entries are added
  useEffect(() => {
    if (progressLogEndRef.current) {
      progressLogEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [progressLog]);

  // Stream progress updates via SSE so the UI reflects backend status in real time.
  const startProgressStream = useCallback(
    (requestId: string) => {
      if (!requestId) {
        return;
      }

      closeEventSource();
      hasCompletedRef.current = false;

      try {
        if (typeof window === 'undefined' || typeof EventSource === 'undefined') {
          console.warn('Server-sent events are not supported in this environment.');
          return;
        }
        const streamUrl = `${API_BASE_URL}/progress/${requestId}`;
        const source = new EventSource(streamUrl);
        eventSourceRef.current = source;

        source.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data) as {
              visit_id?: string;
              status?: string;
              progress?: number;
              timestamp?: number;
              soap_note?: string;
              transcript?: string;
              generation_time?: number;
              audio_duration?: number;
              transcription_time?: number;
              error?: string;
              current_chunk?: number;
              total_chunks?: number;
              chunk_status?: string;
              chunk_text?: string;
            };

            const status = payload?.status;
            const progressValue = payload?.progress || 0;

            // Extract chunk information if available and all required fields are present
            const chunkInfo = (
              payload.current_chunk &&
              payload.total_chunks &&
              payload.chunk_status &&
              typeof payload.current_chunk === 'number' &&
              typeof payload.total_chunks === 'number'
            ) ? {
              current: payload.current_chunk,
              total: payload.total_chunks,
              status: payload.chunk_status,
              text: payload.chunk_text
            } : undefined;

            // Update progress state
            setProgress(progressValue);

            // Debug logging
            console.log('SSE received:', {
              status,
              progress: progressValue,
              visit_id: payload.visit_id,
              chunk: chunkInfo
            });

            // Update status based on backend status
            if (status === 'processing' || status === 'analyzing_audio' ||
              status === 'extracting_text' || status === 'generating_soap' ||
              status === 'finalizing') {
              setStatus('processing');
            } else if (status === 'completed') {
              setStatus('completed');
            } else if (status === 'error') {
              setStatus('error');
            }

            // Update progress log with meaningful messages including chunk info
            const progressMessage = getProgressMessage(status, progressValue, chunkInfo);
            if (progressMessage && progressMessage.trim()) {
              setProgressLog((prev) => {
                // Check if this is a duplicate of the last message
                const lastMessage = prev[prev.length - 1];
                if (lastMessage === progressMessage) {
                  return prev;
                }

                // Check if we need to replace the last message or add a new one
                const shouldReplace = lastMessage && (
                  // Replace "Uploading audio..." with "Audio uploaded successfully"
                  (lastMessage === 'Uploading audio...' &&
                    progressMessage === 'Audio uploaded successfully') ||
                  // Replace "Generating transcript..." with itself (for progress updates)
                  (lastMessage.includes('Generating transcript...') &&
                    progressMessage.includes('Generating transcript...')) ||
                  // Replace "Generating SOAP note..." with itself (for progress updates)
                  (lastMessage.includes('Generating SOAP note...') &&
                    progressMessage.includes('Generating SOAP note...'))
                );

                if (shouldReplace) {
                  // Update the last message (for progress updates on same step)
                  return [...prev.slice(0, -1), progressMessage];
                }

                // Replace "Uploading audio..." when transcript generation starts
                if (progressMessage === 'Generating transcript...' &&
                  prev.includes('Uploading audio...')) {
                  const withoutUploading = prev.filter(msg => msg !== 'Uploading audio...');
                  return [...withoutUploading, 'Audio uploaded successfully', progressMessage];
                }

                // Add "Transcription generated successfully" when transitioning to SOAP generation
                if (progressMessage === 'Generating SOAP note...' &&
                  !prev.includes('Transcription generated successfully') &&
                  prev.some(msg => msg.includes('Generating transcript...'))) {
                  // Replace "Generating transcript..." with "Transcription generated successfully"
                  const withoutTranscript = prev.filter(msg => !msg.includes('Generating transcript...'));
                  return [...withoutTranscript, 'Transcription generated successfully', progressMessage];
                }

                // Add "Transcription generated successfully" when completing (if not already added)
                if (progressMessage === 'SOAP note generated successfully' &&
                  !prev.includes('Transcription generated successfully')) {
                  // Replace "Generating transcript..." and "Generating SOAP note..." with completion messages
                  const cleaned = prev.filter(msg =>
                    !msg.includes('Generating transcript...') &&
                    !msg.includes('Generating SOAP note...')
                  );
                  return [...cleaned, 'Transcription generated successfully', progressMessage];
                }

                // Replace "Generating SOAP note..." when completing
                if (progressMessage === 'SOAP note generated successfully' &&
                  prev.some(msg => msg.includes('Generating SOAP note...'))) {
                  const withoutSoap = prev.filter(msg => !msg.includes('Generating SOAP note...'));
                  return [...withoutSoap, progressMessage];
                }

                return [...prev, progressMessage];
              });
            }

            // Handle completion
            if (status === 'completed' && payload.soap_note) {
              setSoapNote(payload.soap_note);

              // Set transcript and duration data directly from SSE if available
              if (payload.transcript) {
                setTranscript(payload.transcript);
              }

              // Set all duration information from the completion payload
              const audioDuration = payload.audio_duration || 0;
              const transcriptionTime = payload.transcription_time || 0;
              const generationTime = payload.generation_time || 0;
              const totalTime = transcriptionTime + generationTime;

              console.log('Setting durations from SSE:', {
                audioDuration,
                transcriptionTime,
                generationTime,
                totalTime
              });

              setDurations({
                audio_duration_seconds: audioDuration,
                transcription_seconds: transcriptionTime,
                generation_seconds: generationTime,
                total_seconds: totalTime,
              });

              setTimerActive(false);
              hasCompletedRef.current = true;
              if (startTimeRef.current !== null) {
                const finalElapsed = (performance.now() - startTimeRef.current) / 1000;
                setElapsed(finalElapsed);
              }
              startTimeRef.current = null;
              closeEventSource();
              formRef.current?.reset();
              setSelectedFileName(null);
              if (selectedFileUrl) {
                URL.revokeObjectURL(selectedFileUrl);
                setSelectedFileUrl(null);
              }

              // If we didn't get transcript from SSE, fetch from GET endpoint as fallback
              if (!payload.transcript) {
                fetchCompletedVisitData(payload.visit_id);
              }
            }

            // Handle errors
            if (status === 'error') {
              setError(payload.error || 'Processing failed');
              setTimerActive(false);
              setProgress(0);
              hasCompletedRef.current = true;
              closeEventSource();
            }

          } catch (err) {
            console.error('Failed to parse SSE event', err);
          }
        };

        source.onerror = (event) => {
          if (source.readyState === EventSource.CLOSED && !hasCompletedRef.current) {
            console.error('Progress stream closed unexpectedly', event);
            closeEventSource();
            setProgress(0);
            setTimerActive(false);
            if (startTimeRef.current !== null) {
              setElapsed((performance.now() - startTimeRef.current) / 1000);
            }
            startTimeRef.current = null;
          }
        };
      } catch (err) {
        console.error('Failed to establish progress stream', err);
      }
    },
    [closeEventSource, fetchCompletedVisitData, selectedFileUrl],
  );

  const metrics = useMemo(() => {
    if (!durations) {
      return [];
    }

    return [
      { label: 'Audio length', value: formatDuration(durations.audio_duration_seconds) },
      { label: 'Transcription', value: formatSeconds(durations.transcription_seconds) },
      { label: 'SOAP generation', value: formatSeconds(durations.generation_seconds) },
      { label: 'Total time', value: formatSeconds(durations.total_seconds) },
    ];
  }, [durations]);

  // Helper function to render message with animated ellipsis
  const renderMessageWithEllipsis = (message: string) => {
    if (!message.includes('...')) {
      return message;
    }
    const dots = '.'.repeat((ellipsisFrame % 3) + 1);
    return message.replace('...', dots);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    // Clean up previous URL if it exists
    if (selectedFileUrl) {
      URL.revokeObjectURL(selectedFileUrl);
    }

    if (file) {
      setSelectedFileName(file.name);
      setSelectedFileUrl(URL.createObjectURL(file));
    } else {
      setSelectedFileName(null);
      setSelectedFileUrl(null);
    }

    setError(null);
  };

  const handleCopySoapNote = async () => {
    if (!soapNote) return;

    try {
      await navigator.clipboard.writeText(soapNote);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = soapNote;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
      } catch (fallbackErr) {
        console.error('Fallback copy failed:', fallbackErr);
      }
      document.body.removeChild(textArea);
    }
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const formData = new FormData(event.currentTarget);
    const audio = formData.get('audio');

    if (!(audio instanceof File) || audio.size === 0) {
      setError('Please choose an audio recording before generating.');
      setStatus('error');
      setProgress(0);
      return;
    }

    setStatus('processing');
    setError(null);
    setSoapNote('');
    setTranscript('');
    setProgressLog(['Creating visit...']);
    setDurations(null);
    setElapsed(0);
    setProgress(0);
    startTimeRef.current = performance.now();
    setTimerActive(true);
    hasCompletedRef.current = false;

    startTransition(async () => {
      try {
        // Step 1: Create visit and get visit ID
        const visitRes = await fetch(`${API_BASE_URL}/visit`, {
          method: 'POST',
          cache: 'no-store',
        });

        if (!visitRes.ok) {
          throw new Error('Failed to create visit');
        }

        const visitData = await visitRes.json() as { visit_id: string };
        const visitId = visitData.visit_id;

        // Step 2: Start SSE streaming with the visit ID
        startProgressStream(visitId);

        // Wait a moment for SSE connection to establish
        await new Promise(resolve => setTimeout(resolve, 500));

        // Step 3: Upload audio file
        setProgressLog(['Visit created successfully', 'Uploading audio...']);
        const result = await generateSoapNoteAction(formData, visitId);

        if (!result || !result.success) {
          const message = result?.error ?? 'Unable to upload audio file.';
          if (!hasCompletedRef.current) {
            setStatus('error');
            setError(message);
            setProgress(0);
            setTimerActive(false);
            if (startTimeRef.current !== null) {
              const diff = (performance.now() - startTimeRef.current) / 1000;
              setElapsed(diff);
            }
            startTimeRef.current = null;
            hasCompletedRef.current = true;
            closeEventSource();
          }
          return;
        }

        // Audio uploaded successfully, SSE will handle the rest
        // Don't set progress log here, let SSE handle it
      } catch (err) {
        console.error('SOAP generation request failed', err);
        if (!hasCompletedRef.current) {
          setStatus('error');
          setError('Something unexpected occurred. Please try again.');
          setProgress(0);
          setTimerActive(false);
          if (startTimeRef.current !== null) {
            const diff = (performance.now() - startTimeRef.current) / 1000;
            setElapsed(diff);
          }
          startTimeRef.current = null;
          hasCompletedRef.current = true;
          closeEventSource();
        }
      }
    });
  };

  const StatusIcon = statusIconMap[status];
  const elapsedLabel = status === 'idle' && elapsed === 0 ? '--' : formatSeconds(elapsed);

  return (
    <section className="flex-1 min-h-0 space-y-6 lg:grid lg:grid-cols-3 lg:gap-6 lg:space-y-0">
      <Card className="flex flex-col overflow-hidden">
        <CardHeader className="shrink-0">
          <CardTitle className="text-lg font-semibold">System Information</CardTitle>
          <CardDescription>
            Hardware and runtime context sourced from the backend service.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 min-h-0 flex flex-col">
          {systemInfo ? (
            <div className="grid grid-cols-2 gap-3 flex-1" style={{ gridAutoRows: '1fr' }}>
              {SYSTEM_INFO_FIELDS.map(({ key, label, icon: Icon }) => {
                const value = systemInfo?.[key];
                return (
                  <div key={key} className="rounded-md border bg-muted/40 p-3 flex flex-col">
                    <div className="flex items-center gap-2">
                      <Icon className="h-3 w-3 text-muted-foreground" />
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">
                        {label}
                      </p>
                    </div>
                    <p className="mt-1 text-sm font-medium">
                      {value !== undefined && value !== null && value !== ''
                        ? String(value)
                        : '—'}
                    </p>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              Unable to retrieve system information. Confirm the API server is running.
            </p>
          )}
        </CardContent>
      </Card>

      <Card className="flex flex-col overflow-hidden">
        <CardHeader className="shrink-0">
          <CardTitle className="text-lg font-semibold">Upload Visit Audio</CardTitle>
          <CardDescription>
            Attach the recorded visit to generate a transcript and SOAP note.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex-1 min-h-0 flex flex-col space-y-5 overflow-hidden">
          <form ref={formRef} onSubmit={handleSubmit} className="space-y-5 shrink-0">
            <div className="space-y-2">
              <Label htmlFor="audio">Audio file</Label>
              <Input
                id="audio"
                name="audio"
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                disabled={isPending}
              />
              <p className="flex items-center gap-2 text-xs text-muted-foreground">
                <FileAudio className="size-4" />
                {selectedFileName ?? 'Supported formats: WAV, MP3, M4A and other common audio files.'}
              </p>
            </div>

            {error && (
              <p className="flex items-center gap-2 text-sm text-destructive">
                <AlertCircle className="size-5" />
                {error}
              </p>
            )}

            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" disabled={isPending || status === 'processing'} className="gap-2">
                {isPending || status === 'processing' ? (
                  <>
                    <Spinner />
                    Processing...
                  </>
                ) : (
                  'Generate SOAP Note'
                )}
              </Button>

              <Badge variant={statusVariantMap[status]} className="flex items-center gap-1.5">
                <StatusIcon className="size-3.5" />
                {statusLabelMap[status]}
              </Badge>

              <span className="flex items-center gap-1 text-sm text-muted-foreground">
                <Clock3 className="size-4" />
                {elapsedLabel}
              </span>
            </div>

            {selectedFileUrl && selectedFileName && (
              <Card className="border-dashed p-4 flex flex-col gap-2">
                <div className="flex items-center gap-2">
                  <Play className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium text-muted-foreground">Audio File Preview</span>
                </div>
                <p className="text-sm font-medium truncate" title={selectedFileName}>
                  {selectedFileName}
                </p>
                <audio
                  controls
                  className="w-full h-8"
                  src={selectedFileUrl}
                  preload="metadata"
                >
                  Your browser does not support the audio element.
                </audio>
              </Card>
            )}

            {((status === 'processing' && progress > 0) || (status === 'completed' && progress >= 100)) && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Processing Progress</span>
                  </div>
                  <span className="font-medium">{status === 'completed' ? '100' : progress}%</span>
                </div>
                <Progress value={status === 'completed' ? 100 : progress} className="w-full" />
              </div>
            )}
          </form>

          <div className="flex-1 min-h-0 flex flex-col space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium shrink-0">
              <ClipboardList className="size-4" />
              Progress log
            </div>
            <div className="flex-1 min-h-0 overflow-hidden">
              <ScrollArea className="h-full rounded-lg border bg-muted/30">
                <div className="px-4 py-3">
                  {progressLog.length ? (
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      {progressLog.map((entry, index) => {
                        // Check if this is the final success message for special styling
                        const isSoapSuccess = entry === 'SOAP note generated successfully';
                        // Render with animated ellipsis
                        const displayText = renderMessageWithEllipsis(entry);

                        return (
                          <li
                            key={`${entry}-${index}`}
                            className={`leading-relaxed ${isSoapSuccess ? 'text-green-600 dark:text-green-400 font-medium' : ''
                              }`}
                          >
                            {displayText}
                          </li>
                        );
                      })}
                      <div ref={progressLogEndRef} />
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      Status updates will appear here once processing begins.
                    </p>
                  )}
                </div>
              </ScrollArea>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="flex flex-col overflow-hidden">
        <CardHeader className="gap-4 pb-2 shrink-0">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <CardTitle className="text-lg font-semibold">SOAP Note Output</CardTitle>
              <CardDescription>
                Review, copy, or refine the generated documentation.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex items-center border rounded-md">
                <Button
                  variant={viewMode === 'markdown' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('markdown')}
                  className="rounded-r-none"
                  disabled={!soapNote}
                >
                  <Eye className="size-4 mr-1.5" />
                  Preview
                </Button>
                <Button
                  variant={viewMode === 'raw' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('raw')}
                  className="rounded-l-none"
                  disabled={!soapNote}
                >
                  <FileText className="size-4 mr-1.5" />
                  Raw
                </Button>
              </div>
              <Dialog>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm" disabled={!transcript}>
                    View transcript
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-[90vw] w-[90vw]">
                  <DialogHeader>
                    <DialogTitle>Visit Transcript</DialogTitle>
                    <DialogDescription>
                      Generated in {formatSeconds(durations?.transcription_seconds)}.
                    </DialogDescription>
                  </DialogHeader>
                  <ScrollArea className="max-h-[60vh] w-full rounded-lg border bg-muted/40 p-4">
                    {status === 'processing' && !transcript ? (
                      <div className="flex items-center justify-center py-8">
                        <div className="text-center space-y-2">
                          <Spinner className="mx-auto" />
                          <p className="text-sm text-muted-foreground">
                            Transcript is being generated...
                          </p>
                        </div>
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
                        {transcript || 'Transcript will appear once the audio has been processed.'}
                      </p>
                    )}
                  </ScrollArea>
                </DialogContent>
              </Dialog>
              <Button
                variant="outline"
                size="sm"
                disabled={!soapNote}
                onClick={handleCopySoapNote}
                className="gap-1.5"
              >
                {isCopied ? (
                  <>
                    <Check className="size-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="size-4" />
                    Copy SOAP
                  </>
                )}
              </Button>
            </div>
          </div>

          {metrics.length > 0 && (
            <div className="grid gap-2 sm:grid-cols-2">
              {metrics.map(({ label, value }) => (
                <div
                  key={label}
                  className="rounded-md border border-border/60 bg-muted/20 px-3 py-2 text-xs uppercase tracking-wide text-muted-foreground"
                >
                  <div className="flex items-center justify-between">
                    <span>{label}</span>
                    <span className="text-foreground text-sm font-semibold normal-case">
                      {value}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden pt-0">
          {viewMode === 'markdown' ? (
            <ScrollArea className="h-full w-full rounded-lg border bg-background/80 p-4">
              {status === 'processing' ? (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Skeleton className="h-6 w-3/4" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-5/6" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-2/3" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-4/5" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-1/2" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-5/6" />
                  </div>
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-3/5" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                  </div>
                </div>
              ) : soapNote ? (
                <div className="prose prose-sm dark:prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {soapNote}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  The generated SOAP note will appear here.
                </p>
              )}
            </ScrollArea>
          ) : (
            <Textarea
              value={soapNote}
              readOnly
              placeholder="The generated SOAP note will appear here."
              className="h-full resize-none bg-background/80"
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
