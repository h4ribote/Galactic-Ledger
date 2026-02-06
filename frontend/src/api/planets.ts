import { api } from './client';

export interface Planet {
  id: number;
  name: string;
  x: number;
  y: number;
  slots: number;
  owner_id: number | null;
}

export const fetchPlanets = async (): Promise<Planet[]> => {
  const response = await api.get<Planet[]>('/planets/');
  return response.data;
};
