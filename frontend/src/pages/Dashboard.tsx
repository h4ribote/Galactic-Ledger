import { AppShell, Burger, Group, Title, Container, Table, Text, Loader, Center, Button } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQuery } from '@tanstack/react-query';
import { fetchPlanets } from '../api/planets';
import { useAuth } from '../context/AuthContext';

function PlanetList() {
  const { data: planets, isLoading, error } = useQuery({
    queryKey: ['planets'],
    queryFn: fetchPlanets,
  });

  if (isLoading) return <Center h={200}><Loader /></Center>;
  if (error) return <Text c="red">Error loading planets: {error.message}</Text>;

  const rows = planets?.map((planet: any) => (
    <Table.Tr key={planet.id}>
      <Table.Td>{planet.id}</Table.Td>
      <Table.Td>{planet.name}</Table.Td>
      <Table.Td>({planet.x}, {planet.y})</Table.Td>
      <Table.Td>{planet.slots}</Table.Td>
    </Table.Tr>
  ));

  return (
    <Table>
      <Table.Thead>
        <Table.Tr>
          <Table.Th>ID</Table.Th>
          <Table.Th>Name</Table.Th>
          <Table.Th>Coordinates</Table.Th>
          <Table.Th>Slots</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>{rows}</Table.Tbody>
    </Table>
  );
}

export function Dashboard() {
  const [opened, { toggle }] = useDisclosure();
  const { logout, user } = useAuth();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <Title order={3}>Galactic Ledger</Title>
          </Group>
          <Group>
            <Text>{user?.username}</Text>
            <Button variant="light" onClick={logout}>Logout</Button>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <Text>Navigation</Text>
        {/* Navigation links will go here */}
      </AppShell.Navbar>

      <AppShell.Main>
        <Container>
          <Title order={2} mb="md">Planets</Title>
          <PlanetList />
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}
