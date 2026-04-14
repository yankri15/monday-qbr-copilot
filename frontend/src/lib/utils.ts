export function cn(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

export function slugToAccountName(slug: string) {
  return decodeURIComponent(slug);
}

export function accountNameToSlug(name: string) {
  return encodeURIComponent(name);
}
