import { useState } from 'react';
import { TextInput, Button, Container, Title, Paper, Divider, Text } from '@mantine/core';
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
    <Container size={420} my={40}>
      <Title ta="center">Welcome back!</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>
        Sign in to Galactic Ledger
      </Text>

      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={handleDevLogin}>
          <TextInput
            label="Dev Login (Username)"
            placeholder="Your username"
            required
            value={username}
            onChange={(e) => setUsername(e.currentTarget.value)}
          />
          <Button fullWidth mt="xl" type="submit" loading={loading}>
            Dev Login
          </Button>
        </form>

        <Divider label="Or continue with" labelPosition="center" my="lg" />

        <Button
          component="a"
          href={getDiscordLoginUrl()}
          fullWidth
          variant="outline"
        >
          Discord
        </Button>
      </Paper>
    </Container>
  );
}
