// src/app/register/page.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Button, Container, TextField, Typography, Link as MuiLink,
  Snackbar, Alert
} from '@mui/material';
import NextLink from 'next/link';
import api from '@/services/api';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setNotification(null);

    try {
      await api.post('/register', { username, email, password });
      setNotification({ type: 'success', message: 'Registration successful! Redirecting to login...' });
      setTimeout(() => router.push('/'), 2000);
    } catch (err) {
      setNotification({ type: 'error', message: 'Registration failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">
          Sign up
        </Typography>
        <Box component="form" onSubmit={handleRegister} sx={{ mt: 3 }}>
          <TextField margin="normal" required fullWidth id="username" label="Username" name="username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <TextField margin="normal" required fullWidth id="email" label="Email Address" name="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <TextField margin="normal" required fullWidth name="password" label="Master Password" type="password" id="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }} disabled={isLoading}>
            {isLoading ? 'Registering...' : 'Sign Up'}
          </Button>
          <MuiLink component={NextLink} href="/" variant="body2" sx={{ textAlign: 'center', display: 'block' }}>
            {"Already have an account? Sign in"}
          </MuiLink>
        </Box>
      </Box>
      <Snackbar open={!!notification} autoHideDuration={6000} onClose={() => setNotification(null)}>
        <Alert onClose={() => setNotification(null)} severity={notification?.type} sx={{ width: '100%' }}>
          {notification?.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}