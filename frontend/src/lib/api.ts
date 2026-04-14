import type { Account, GenerateEvent, GenerateQbrHandlers } from "@/lib/types";

function getApiBaseUrl() {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }

  return "http://127.0.0.1:8000";
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
  accountName: string,
  handlers: GenerateQbrHandlers,
) {
  const response = await fetch(`${getApiBaseUrl()}/api/generate-qbr`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({
      account_name: accountName,
    }),
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

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value, { stream: !done });

    const messages = buffer.split("\n\n");
    buffer = messages.pop() ?? "";

    for (const message of messages) {
      const parsed = parseSseChunk(message);
      if (!parsed) {
        continue;
      }

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
      break;
    }
  }
}
