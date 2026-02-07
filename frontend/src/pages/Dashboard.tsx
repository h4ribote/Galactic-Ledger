import { AppShell, Burger, Group, Title, Container, Table, Text, Loader, Center, Button, Tabs, Box, Badge, Stack } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useQuery } from '@tanstack/react-query';
import { fetchPlanets } from '../api/planets';
import { useAuth } from '../context/AuthContext';
import { FleetList } from '../components/FleetList';
import { GalaxyMap } from '../features/map/GalaxyMap';
import { IconMap, IconPlanet, IconRocket, IconLogout, IconUser } from '@tabler/icons-react';

function PlanetList() {
  const { data: planets, isLoading, error } = useQuery({
    queryKey: ['planets'],
    queryFn: fetchPlanets,
  });

  if (isLoading) return <Center h={200}><Loader color="brand" /></Center>;
  if (error) return <Text c="red">Error loading planets: {error.message}</Text>;

  const rows = planets?.map((planet) => (
    <Table.Tr key={planet.id}>
      <Table.Td style={{ color: '#00f2ff' }}>{planet.id}</Table.Td>
      <Table.Td>{planet.name}</Table.Td>
      <Table.Td style={{ fontFamily: 'JetBrains Mono' }}>
        [{planet.x}, {planet.y}]
      </Table.Td>
      <Table.Td>
        <Badge color="dark" variant="outline" radius="sm">{planet.slots} SLOTS</Badge>
      </Table.Td>
    </Table.Tr>
  ));

  return (
    <Box className="glass" p="md">
        <Group justify="space-between" mb="md" className="panel-header">
            <Text fw={700}>PLANETARY DATABASE</Text>
            <Badge color="brand" variant="dot">LIVE FEED</Badge>
        </Group>
        <Table verticalSpacing="sm" withTableBorder={false}>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>DESIGNATION</Table.Th>
              <Table.Th>COORDINATES</Table.Th>
              <Table.Th>CAPACITY</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>{rows}</Table.Tbody>
        </Table>
    </Box>
  );
}

export function Dashboard() {
  const [opened, { toggle }] = useDisclosure();
  const { logout, user } = useAuth();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 250,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between" style={{ borderBottom: '1px solid rgba(0, 242, 255, 0.2)' }}>
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" color="#00f2ff" />
            <Title order={3} style={{ fontFamily: 'Rajdhani', letterSpacing: '2px', color: '#00f2ff' }}>
                GL // OS <span style={{ fontSize: '0.6em', color: '#666' }}>v1.0</span>
            </Title>
          </Group>
          <Group gap="xs">
            <IconUser size={18} color="#00f2ff" />
            <Text size="sm" ff="monospace" c="dimmed" mr="md">
                CMD // {user?.username?.toUpperCase()}
            </Text>
            <Button
                variant="subtle"
                color="red"
                size="xs"
                onClick={logout}
                leftSection={<IconLogout size={14} />}
                style={{ border: '1px solid rgba(255, 50, 50, 0.3)' }}
            >
                TERMINATE
            </Button>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md" style={{ borderRight: '1px solid rgba(0, 242, 255, 0.1)' }}>
        <Stack gap="xs">
            <Text size="xs" c="dimmed" mb="xs" tt="uppercase" style={{ letterSpacing: '1px' }}>Modules</Text>
            {/* Ideally these buttons would control the tabs or routing, currently tabs are local state */}
            <Button variant="light" color="brand" justify="flex-start" leftSection={<IconMap size={16} />}>GALAXY MAP</Button>
            <Button variant="subtle" color="gray" justify="flex-start" leftSection={<IconPlanet size={16} />}>PLANETS</Button>
            <Button variant="subtle" color="gray" justify="flex-start" leftSection={<IconRocket size={16} />}>FLEETS</Button>
        </Stack>

        <Box mt="auto">
            <Box p="xs" style={{ border: '1px solid rgba(255, 255, 255, 0.1)', background: 'rgba(0,0,0,0.3)' }}>
                <Text size="xs" c="dimmed" ta="center" ff="monospace">SERVER STATUS: OK</Text>
                <Text size="xs" c="brand" ta="center" ff="monospace">PING: 12ms</Text>
            </Box>
        </Box>
      </AppShell.Navbar>

      <AppShell.Main>
        <Container size="xl" fluid>
          <Tabs defaultValue="map" variant="pills" color="brand" radius={0}>
            <Tabs.List mb="md" grow>
              <Tabs.Tab value="map" leftSection={<IconMap size={14} />}>TACTICAL MAP</Tabs.Tab>
              <Tabs.Tab value="planets" leftSection={<IconPlanet size={14} />}>PLANETARY DATA</Tabs.Tab>
              <Tabs.Tab value="fleets" leftSection={<IconRocket size={14} />}>FLEET COMMAND</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="map">
              <Box className="glass" p={2} style={{ border: '1px solid #00f2ff', boxShadow: '0 0 10px rgba(0, 242, 255, 0.1)' }}>
                 <GalaxyMap />
              </Box>
            </Tabs.Panel>

            <Tabs.Panel value="planets">
              <PlanetList />
            </Tabs.Panel>

            <Tabs.Panel value="fleets">
              <Box className="glass" p="md">
                 <Group justify="space-between" mb="md" className="panel-header">
                    <Text fw={700}>ACTIVE FLEETS</Text>
                    <Badge color="orange" variant="outline">RESTRICTED</Badge>
                </Group>
                <FleetList />
              </Box>
            </Tabs.Panel>
          </Tabs>
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}
