import { hosted, fixturePath } from "./hosting";

export async function request<T>(
  path: string,
  signal?: AbortSignal,
): Promise<T> {
  const target = hosted ? import.meta.env.BASE_URL + fixturePath(path) : path;
  const response = await fetch(target, { signal });
  if (!response.ok) throw new Error("This local preview could not load.");
  return response.json() as Promise<T>;
}
