import type {
  Account,
  GenerateEvent,
  GenerateQbrHandlers,
  GenerateQbrPayload,
  UploadDataResponse,
} from "@/lib/types";
import { downloadBlob } from "@/lib/export";

function getApiBaseUrl() {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  if (typeof window !== "undefined") {
    const { protocol, hostname } = window.location;
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return `${protocol}//${hostname}:8000`;
    }

    return "";
  }

  return process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "";
}

async function parseJsonError(response: Response) {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail ?? `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
}

function parseSseChunk(chunk: string) {
  const lines = chunk.split("\n");
  const dataLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trim());
    }
  }

  const payload = dataLines.join("\n");
  if (!payload) {
    return null;
  }

  return {
    data: JSON.parse(payload) as GenerateEvent,
  };
}

export async function fetchAccounts() {
  const response = await fetch(`${getApiBaseUrl()}/api/accounts`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await parseJsonError(response));
  }

  return (await response.json()) as Account[];
}

export async function uploadAccountsFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${getApiBaseUrl()}/api/upload-data`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseJsonError(response));
  }

  return (await response.json()) as UploadDataResponse;
}

export async function refineQBR(draft: string, instructions: string) {
  const response = await fetch(`${getApiBaseUrl()}/api/refine-qbr`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      current_draft: draft,
      instructions,
    }),
  });

  if (!response.ok) {
    throw new Error(await parseJsonError(response));
  }

  const payload = (await response.json()) as { refined_draft: string };
  return payload.refined_draft;
}

export async function generateQBR(
  payload: GenerateQbrPayload,
  handlers: GenerateQbrHandlers,
) {
  const response = await fetch(`${getApiBaseUrl()}/api/generate-qbr`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await parseJsonError(response));
  }

  if (!response.body) {
    throw new Error("The QBR stream did not return a readable response body.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  // #region agent log
  const _dbgStart = Date.now();
  let _dbgReadCount = 0;
  let _dbgEventCount = 0;
  fetch('http://127.0.0.1:7610/ingest/4e46dfaf-ab6a-458e-a117-1dee12909194',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'8ee21d'},body:JSON.stringify({sessionId:'8ee21d',location:'api.ts:stream_start',message:'SSE stream opened',data:{t:_dbgStart},timestamp:Date.now(),hypothesisId:'H-A'})}).catch(()=>{});
  // #endregion

  while (true) {
    // #region agent log
    const _dbgReadT = Date.now();
    // #endregion
    const { done, value } = await reader.read();
    buffer += decoder.decode(value, { stream: !done });

    const messages = buffer.split("\n\n");
    buffer = messages.pop() ?? "";

    // #region agent log
    _dbgReadCount++;
    const _dbgEventsInChunk = messages.filter(m => m.includes('data:')).length;
    if (_dbgEventsInChunk > 0) {
      fetch('http://127.0.0.1:7610/ingest/4e46dfaf-ab6a-458e-a117-1dee12909194',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'8ee21d'},body:JSON.stringify({sessionId:'8ee21d',location:'api.ts:read_chunk',message:'SSE chunk received',data:{readN:_dbgReadCount,eventsInChunk:_dbgEventsInChunk,elapsedMs:_dbgReadT-_dbgStart,done},timestamp:Date.now(),hypothesisId:'H-A'})}).catch(()=>{});
    }
    // #endregion

    for (const message of messages) {
      const parsed = parseSseChunk(message);
      if (!parsed) {
        continue;
      }

      // #region agent log
      _dbgEventCount++;
      fetch('http://127.0.0.1:7610/ingest/4e46dfaf-ab6a-458e-a117-1dee12909194',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'8ee21d'},body:JSON.stringify({sessionId:'8ee21d',location:'api.ts:event',message:'SSE event received',data:{n:_dbgEventCount,type:parsed.data.type,elapsedMs:Date.now()-_dbgStart},timestamp:Date.now(),hypothesisId:'H-B'})}).catch(()=>{});
      // #endregion

      handlers.onEvent?.(parsed.data);

      if (parsed.data.type === "TEXT_MESSAGE_CONTENT") {
        handlers.onDraftChunk?.(parsed.data.delta);
      }

      if (parsed.data.type === "RUN_ERROR") {
        throw new Error(parsed.data.message);
      }

      if (parsed.data.type === "RUN_FINISHED") {
        handlers.onComplete?.();
      }
    }

    if (done) {
      // #region agent log
      fetch('http://127.0.0.1:7610/ingest/4e46dfaf-ab6a-458e-a117-1dee12909194',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'8ee21d'},body:JSON.stringify({sessionId:'8ee21d',location:'api.ts:stream_done',message:'SSE stream ended',data:{totalReads:_dbgReadCount,totalEvents:_dbgEventCount,totalElapsedMs:Date.now()-_dbgStart},timestamp:Date.now(),hypothesisId:'H-A'})}).catch(()=>{});
      // #endregion
      break;
    }
  }
}

export async function exportPdf(markdownContent: string, accountName: string) {
  const response = await fetch(`${getApiBaseUrl()}/api/export-pdf`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      markdown_content: markdownContent,
      account_name: accountName,
    }),
  });

  if (!response.ok) {
    throw new Error(await parseJsonError(response));
  }

  const blob = await response.blob();
  downloadBlob(blob, accountName, "pdf");
}
