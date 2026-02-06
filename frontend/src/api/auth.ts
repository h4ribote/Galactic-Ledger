import { client } from './client';

export interface User {
  id: number;
  username: string;
  avatar_url?: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export async function devLogin(username: string): Promise<LoginResponse> {
  const response = await client.post<LoginResponse>('/auth/dev-login', { username });
  return response.data;
}

export function getDiscordLoginUrl(): string {
  // baseURL might have /api/v1 suffix, check if it ends with /
  const baseURL = client.defaults.baseURL || '';
  return `${baseURL}/auth/login`;
}

export async function getMe(): Promise<User> {
  const response = await client.get<User>('/users/me');
  return response.data;
}
