import { client } from './client';

export interface Fleet {
  id: number;
  owner_id: number;
  name: string;
  location_planet_id: number | null;
  destination_planet_id: number | null;
  arrival_time: string | null;
  status: 'IDLE' | 'TRANSIT' | 'ARRIVED'; // Adjust based on backend exact strings if needed, assuming 'IDLE', 'TRANSIT' from previous reads
  cargo_capacity: number;
  created_at: string;
  updated_at: string | null;
}

export interface FleetCreate {
  name: string;
  location_planet_id: number;
}

export interface FleetUpdate {
  destination_planet_id?: number;
  status?: string;
}

export const fetchFleets = async (skip = 0, limit = 100): Promise<Fleet[]> => {
  const response = await client.get<Fleet[]>('/fleets/', { params: { skip, limit } });
  return response.data;
};

export const createFleet = async (data: FleetCreate): Promise<Fleet> => {
  const response = await client.post<Fleet>('/fleets/', data);
  return response.data;
};

export const moveFleet = async (id: number, data: FleetUpdate): Promise<Fleet> => {
  const response = await client.post<Fleet>(`/fleets/${id}/move`, data);
  return response.data;
};

export const processArrival = async (id: number): Promise<Fleet> => {
  const response = await client.post<Fleet>(`/fleets/${id}/arrive`);
  return response.data;
};
