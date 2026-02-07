import { Table, Button, Group, Text, Loader, Modal, Select, TextInput, Badge } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { fetchFleets, createFleet, moveFleet, processArrival } from '../api/fleets';
import type { Fleet, FleetCreate } from '../api/fleets';
import { fetchPlanets } from '../api/planets';
import { notifications } from '@mantine/notifications';
import { AxiosError } from 'axios';
import { IconRocket, IconArrowRight, IconMapPin } from '@tabler/icons-react';

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

  if (fleetsLoading) return <Loader color="brand" />;

  const rows = fleets?.map((fleet) => {
    const isArrived = fleet.status === 'TRANSIT' && fleet.arrival_time && new Date(fleet.arrival_time) <= new Date();

    return (
      <Table.Tr key={fleet.id}>
        <Table.Td style={{ color: '#00f2ff', fontFamily: 'JetBrains Mono' }}>{fleet.id}</Table.Td>
        <Table.Td style={{ fontWeight: 600 }}>{fleet.name}</Table.Td>
        <Table.Td>
            <Badge
                color={fleet.status === 'TRANSIT' ? 'orange' : 'green'}
                variant="outline"
                size="sm"
            >
                {fleet.status}
            </Badge>
        </Table.Td>
        <Table.Td>
            {fleet.location_planet_id ? (
                <Group gap={4}>
                    <IconMapPin size={14} color="gray" />
                    <Text size="sm">{planetMap.get(fleet.location_planet_id)}</Text>
                </Group>
            ) : '-'}
        </Table.Td>
        <Table.Td>
            {fleet.destination_planet_id ? (
                <Group gap={4}>
                    <IconArrowRight size={14} color="orange" />
                    <Text size="sm">{planetMap.get(fleet.destination_planet_id)}</Text>
                </Group>
            ) : '-'}
        </Table.Td>
        <Table.Td style={{ fontFamily: 'JetBrains Mono', fontSize: '0.85em' }}>
            {fleet.arrival_time ? new Date(fleet.arrival_time).toLocaleString() : '--:--:--'}
        </Table.Td>
        <Table.Td>
          <Group gap={4}>
            {fleet.status === 'IDLE' && (
              <Button
                size="compact-xs"
                variant="light"
                color="brand"
                onClick={() => handleMoveClick(fleet)}
                style={{ border: '1px solid rgba(0, 242, 255, 0.3)' }}
              >
                MOVE
              </Button>
            )}
            {isArrived && (
              <Button size="compact-xs" color="green" variant="filled" onClick={() => handleArriveClick(fleet.id)}>
                ARRIVE
              </Button>
            )}
          </Group>
        </Table.Td>
      </Table.Tr>
    );
  });

  return (
    <>
      <Group justify="flex-end" mb="md">
        <Button onClick={openCreate} leftSection={<IconRocket size={16}/>} color="brand" variant="filled">
            COMMISSION NEW FLEET
        </Button>
      </Group>

      <Table verticalSpacing="sm" withTableBorder={false}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ID</Table.Th>
            <Table.Th>CALLSIGN</Table.Th>
            <Table.Th>STATUS</Table.Th>
            <Table.Th>CURRENT LOC</Table.Th>
            <Table.Th>DESTINATION</Table.Th>
            <Table.Th>ETA / ARRIVAL</Table.Th>
            <Table.Th>COMMAND</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{rows}</Table.Tbody>
      </Table>

      {/* Move Fleet Modal */}
      <Modal opened={openedMove} onClose={closeMove} title={`INITIATE TRANSIT: ${selectedFleet?.name?.toUpperCase()}`}>
        <Select
          label="DESTINATION VECTOR"
          placeholder="Select Target Planet"
          data={planetOptions.filter(p => p.value !== selectedFleet?.location_planet_id?.toString())}
          value={destinationId}
          onChange={setDestinationId}
          mb="md"
        />
        <Button fullWidth onClick={handleConfirmMove} loading={moveMutation.isPending} color="orange">
          ENGAGE HYPERDRIVE
        </Button>
      </Modal>

      {/* Create Fleet Modal */}
      <Modal opened={openedCreate} onClose={closeCreate} title="FLEET COMMISSIONING">
        <TextInput
          label="FLEET DESIGNATION"
          placeholder="Enter fleet name"
          value={newFleetName}
          onChange={(e) => setNewFleetName(e.currentTarget.value)}
          mb="sm"
        />
        <Select
          label="DEPLOYMENT POINT"
          placeholder="Select planet"
          data={planetOptions}
          value={startPlanetId}
          onChange={setStartPlanetId}
          mb="md"
        />
        <Button fullWidth onClick={handleCreate} loading={createMutation.isPending} color="brand">
          COMMISSION
        </Button>
      </Modal>
    </>
  );
}
