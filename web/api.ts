export async function request<T>(
  path: string,
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(path, { signal });
  if (!response.ok) throw new Error("This local preview could not load.");
  return response.json() as Promise<T>;
}
