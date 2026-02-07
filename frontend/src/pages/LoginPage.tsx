import { useState } from 'react';
import { TextInput, Button, Container, Title, Paper, Divider, Text, Box, Center, Stack } from '@mantine/core';
import { useAuth } from '../context/AuthContext';
import { getDiscordLoginUrl } from '../api/auth';
import { useNavigate } from 'react-router-dom';

export function LoginPage() {
  const [username, setUsername] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleDevLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username);
      navigate('/');
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'radial-gradient(circle at center, rgba(11, 23, 40, 0.4) 0%, rgba(11, 13, 20, 1) 70%)'
      }}
    >
      <Container size={460} w="100%">
        <Paper
          withBorder
          shadow="xl"
          p={40}
          radius={0}
          style={{
            backgroundColor: 'rgba(11, 13, 20, 0.8)',
            backdropFilter: 'blur(12px)',
            borderColor: 'rgba(0, 242, 255, 0.3)',
            boxShadow: '0 0 20px rgba(0, 242, 255, 0.1)'
          }}
        >
          <Stack gap="xs" align="center" mb={30}>
            <Text
              c="brand"
              size="xs"
              tt="uppercase"
              style={{ letterSpacing: '3px' }}
            >
              Secure Connection Established
            </Text>
            <Title
              ta="center"
              order={1}
              style={{
                fontFamily: 'Rajdhani, sans-serif',
                textTransform: 'uppercase',
                letterSpacing: '2px',
                color: '#fff'
              }}
            >
              Galactic Ledger
            </Title>
            <Text c="dimmed" size="sm" ta="center">
              Identity Verification Required
            </Text>
          </Stack>

          <form onSubmit={handleDevLogin}>
            <TextInput
              label="Dev Access ID"
              placeholder="ENTER USERNAME"
              required
              value={username}
              onChange={(e) => setUsername(e.currentTarget.value)}
              variant="filled"
              styles={{
                input: {
                  backgroundColor: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: '#00f2ff',
                  fontFamily: 'JetBrains Mono, monospace',
                  letterSpacing: '1px',
                  '&:focus': {
                    borderColor: '#00f2ff',
                  }
                },
                label: {
                  color: '#888',
                  marginBottom: 8
                }
              }}
            />
            <Button
              fullWidth
              mt="xl"
              type="submit"
              loading={loading}
              variant="filled"
              color="brand"
              style={{
                backgroundColor: 'rgba(0, 242, 255, 0.1)',
                border: '1px solid #00f2ff',
                color: '#00f2ff',
                height: '42px',
                '&:hover': {
                    backgroundColor: 'rgba(0, 242, 255, 0.2)',
                    boxShadow: '0 0 15px rgba(0, 242, 255, 0.4)'
                }
              }}
            >
              INITIALIZE SESSION
            </Button>
          </form>

          <Divider label="OR AUTHENTICATE VIA" labelPosition="center" my="lg" color="dark.4" />

          <Button
            component="a"
            href={getDiscordLoginUrl()}
            fullWidth
            variant="outline"
            color="indigo"
            style={{
                borderColor: '#5865F2',
                color: '#5865F2',
                '&:hover': {
                    backgroundColor: 'rgba(88, 101, 242, 0.1)',
                    boxShadow: '0 0 10px rgba(88, 101, 242, 0.3)'
                }
            }}
          >
            DISCORD PROTOCOL
          </Button>
        </Paper>

        <Center mt="xl">
             <Text size="xs" c="dimmed" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                SYSTEM STATUS: ONLINE // VER: 0.0.1
             </Text>
        </Center>
      </Container>
    </Box>
  );
}
