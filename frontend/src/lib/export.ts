function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.rel = "noopener";
  link.style.display = "none";
  document.body.append(link);
  link.click();
  window.setTimeout(() => {
    URL.revokeObjectURL(url);
    link.remove();
  }, 1000);
}

function buildFileName(accountName: string, extension: string) {
  const safeAccountName = accountName.trim().replace(/[^\w -]+/g, "_") || "QBR";
  return `${safeAccountName}_QBR.${extension}`;
}

export function downloadMarkdown(draft: string, accountName: string) {
  const blob = new Blob([draft], { type: "text/markdown;charset=utf-8" });
  triggerDownload(blob, buildFileName(accountName, "md"));
}

export function downloadBlob(blob: Blob, accountName: string, extension: string) {
  triggerDownload(blob, buildFileName(accountName, extension));
}
