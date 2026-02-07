import { Table, Button, Group, Text, Loader, Modal, Select, TextInput } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { fetchFleets, createFleet, moveFleet, processArrival } from '../api/fleets';
import type { Fleet, FleetCreate } from '../api/fleets';
import { fetchPlanets } from '../api/planets';
import { notifications } from '@mantine/notifications';
import { AxiosError } from 'axios';

export function FleetList() {
  const queryClient = useQueryClient();
  const [selectedFleet, setSelectedFleet] = useState<Fleet | null>(null);
  const [destinationId, setDestinationId] = useState<string | null>(null);
  const [openedMove, { open: openMove, close: closeMove }] = useDisclosure(false);
  const [openedCreate, { open: openCreate, close: closeCreate }] = useDisclosure(false);

  // Form state for creating a fleet
  const [newFleetName, setNewFleetName] = useState('');
  const [startPlanetId, setStartPlanetId] = useState<string | null>(null);

  const { data: fleets, isLoading: fleetsLoading } = useQuery({
    queryKey: ['fleets'],
    queryFn: () => fetchFleets(),
  });

  const { data: planets } = useQuery({
    queryKey: ['planets'],
    queryFn: fetchPlanets,
  });

  const createMutation = useMutation({
    mutationFn: (newFleet: FleetCreate) => createFleet(newFleet),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fleets'] });
      notifications.show({ title: 'Success', message: 'Fleet created successfully', color: 'green' });
      closeCreate();
      setNewFleetName('');
      setStartPlanetId(null);
    },
    onError: (error: AxiosError<{ detail: string }>) => {
      notifications.show({ title: 'Error', message: error.response?.data?.detail || 'Failed to create fleet', color: 'red' });
    }
  });

  const moveMutation = useMutation({
    mutationFn: ({ id, destinationId }: { id: number; destinationId: number }) =>
      moveFleet(id, { destination_planet_id: destinationId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fleets'] });
      notifications.show({ title: 'Success', message: 'Fleet is moving', color: 'green' });
      closeMove();
      setSelectedFleet(null);
      setDestinationId(null);
    },
    onError: (error: AxiosError<{ detail: string }>) => {
      notifications.show({ title: 'Error', message: error.response?.data?.detail || 'Failed to move fleet', color: 'red' });
    }
  });

  const arrivalMutation = useMutation({
    mutationFn: (id: number) => processArrival(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fleets'] });
      notifications.show({ title: 'Success', message: 'Fleet has arrived', color: 'green' });
    },
    onError: (error: AxiosError<{ detail: string }>) => {
      notifications.show({ title: 'Error', message: error.response?.data?.detail || 'Failed to process arrival', color: 'red' });
    }
  });

  const handleCreate = () => {
    if (!newFleetName || !startPlanetId) return;
    createMutation.mutate({ name: newFleetName, location_planet_id: parseInt(startPlanetId) });
  };

  const handleMoveClick = (fleet: Fleet) => {
    setSelectedFleet(fleet);
    openMove();
  };

  const handleConfirmMove = () => {
    if (selectedFleet && destinationId) {
      moveMutation.mutate({ id: selectedFleet.id, destinationId: parseInt(destinationId) });
    }
  };

  const handleArriveClick = (id: number) => {
    arrivalMutation.mutate(id);
  };

  const planetOptions = planets?.map(p => ({ value: p.id.toString(), label: p.name })) || [];
  const planetMap = new Map(planets?.map(p => [p.id, p.name]));

  if (fleetsLoading) return <Loader />;

  const rows = fleets?.map((fleet) => {
    const isArrived = fleet.status === 'TRANSIT' && fleet.arrival_time && new Date(fleet.arrival_time) <= new Date();

    return (
      <Table.Tr key={fleet.id}>
        <Table.Td>{fleet.id}</Table.Td>
        <Table.Td>{fleet.name}</Table.Td>
        <Table.Td>{fleet.status}</Table.Td>
        <Table.Td>{fleet.location_planet_id ? planetMap.get(fleet.location_planet_id) : '-'}</Table.Td>
        <Table.Td>{fleet.destination_planet_id ? planetMap.get(fleet.destination_planet_id) : '-'}</Table.Td>
        <Table.Td>{fleet.arrival_time ? new Date(fleet.arrival_time).toLocaleString() : '-'}</Table.Td>
        <Table.Td>
          <Group>
            {fleet.status === 'IDLE' && (
              <Button size="xs" onClick={() => handleMoveClick(fleet)}>Move</Button>
            )}
            {isArrived && (
              <Button size="xs" color="green" onClick={() => handleArriveClick(fleet.id)}>Arrive</Button>
            )}
          </Group>
        </Table.Td>
      </Table.Tr>
    );
  });

  return (
    <>
      <Group justify="space-between" mb="md">
        <Text size="xl" fw={700}>Fleets</Text>
        <Button onClick={openCreate}>Create Fleet</Button>
      </Group>

      <Table>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ID</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Location</Table.Th>
            <Table.Th>Destination</Table.Th>
            <Table.Th>Arrival Time</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>

      {/* Move Fleet Modal */}
      <Modal opened={openedMove} onClose={closeMove} title={`Move Fleet: ${selectedFleet?.name}`}>
        <Select
          label="Destination"
          placeholder="Select planet"
          data={planetOptions.filter(p => p.value !== selectedFleet?.location_planet_id?.toString())}
          value={destinationId}
          onChange={setDestinationId}
          mb="md"
        />
        <Button fullWidth onClick={handleConfirmMove} loading={moveMutation.isPending}>
          Confirm Move
        </Button>
      </Modal>

      {/* Create Fleet Modal */}
      <Modal opened={openedCreate} onClose={closeCreate} title="Create New Fleet">
        <TextInput
          label="Fleet Name"
          placeholder="Enter fleet name"
          value={newFleetName}
          onChange={(e) => setNewFleetName(e.currentTarget.value)}
          mb="sm"
        />
        <Select
          label="Starting Planet"
          placeholder="Select planet"
          data={planetOptions}
          value={startPlanetId}
          onChange={setStartPlanetId}
          mb="md"
        />
        <Button fullWidth onClick={handleCreate} loading={createMutation.isPending}>
          Create Fleet
        </Button>
      </Modal>
    </>
  );
}
