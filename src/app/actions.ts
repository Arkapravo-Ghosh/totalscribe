'use server';

const API_URL = process.env.API_URL ?? "http://localhost:8000";

type MaybeRecord = Record<string, unknown>;

export type SystemInfoResponse = MaybeRecord | null;

export type SoapNoteDurations = {
  transcription_seconds: number;
  generation_seconds: number;
  total_seconds: number;
  audio_duration_seconds: number;
};

export type SoapNotePayload = {
  soap_note: string;
  transcript: string;
  durations: SoapNoteDurations;
  progress_log: string[];
  request_id?: string;
};

export type SoapNoteActionResult =
  | { success: true; data: SoapNotePayload }
  | { success: false; error: string };

async function parseJson<T = MaybeRecord>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return (await response.json()) as T;
  }
  const text = await response.text();
  try {
    return JSON.parse(text) as T;
  } catch {
    return ({ raw: text } as unknown) as T;
  }
}

export async function fetchSystemInfo(): Promise<SystemInfoResponse> {
  try {
    const res = await fetch(`${API_URL}/system-info`, {
      method: "GET",
      cache: "no-store",
    });

    if (!res.ok) {
      const payload = await parseJson(res);
      console.error("Failed to fetch system info", payload);
      return null;
    }

    return (await res.json()) as MaybeRecord;
  } catch (error) {
    console.error("System info request failed", error);
    return null;
  }
}

export async function generateSoapNote(
  formData: FormData,
  visitId?: string,
): Promise<SoapNoteActionResult> {
  try {
    const audio = formData.get("audio");

    if (!(audio instanceof File) || audio.size === 0) {
      return { success: false, error: "Please select an audio recording." };
    }

    if (!visitId) {
      return { success: false, error: "Visit ID is required" };
    }

    // Upload audio for processing
    const payload = new FormData();
    payload.append("audio_file", audio, audio.name ?? "recording.wav");

    const uploadRes = await fetch(`${API_URL}/soap/${visitId}`, {
      method: "POST",
      body: payload,
      cache: "no-store",
    });

    if (!uploadRes.ok) {
      const errorData = await parseJson(uploadRes);
      return { success: false, error: `Failed to upload audio for processing: ${JSON.stringify(errorData)}` };
    }

    // Return success immediately - SSE will handle progress updates
    const data: SoapNotePayload = {
      soap_note: "",
      transcript: "",
      durations: {
        transcription_seconds: 0,
        generation_seconds: 0,
        total_seconds: 0,
        audio_duration_seconds: 0,
      },
      progress_log: [`Audio uploaded for visit ${visitId}`],
      request_id: visitId,
    };
    return { success: true, data };
  } catch (error) {
    console.error("SOAP note generation failed", error);
    return {
      success: false,
      error: "Unexpected error while generating the SOAP note.",
    };
  }
}
