// src/app/register/page.tsx
'use client';

import axios from 'axios';

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
  // The 'email' state has been removed
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);
  const router = useRouter();

const handleRegister = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);
  setNotification(null);

  try {
    await api.post('/register', { username, password });
    setNotification({ type: 'success', message: 'Profile created! Redirecting to login...' });
    setTimeout(() => router.push('/'), 2000);
  } catch (err) {
    // This is the improved error handling block
    if (axios.isAxiosError(err)) {
      if (err.response) {
        // The backend responded with an error status code (4xx or 5xx)
        // This is likely a "username taken" error.
        setNotification({ type: 'error', message: 'Registration failed. That username might be taken.' });
      } else {
        // The request was made, but no response was received
        // This means the backend is offline or unreachable.
        setNotification({ type: 'error', message: 'Failed to connect to the server. Please try again later.' });
      }
    } else {
      // A non-network error occurred
      setNotification({ type: 'error', message: 'An unexpected error occurred.' });
      console.error(err); // Log the unexpected error to the console
    }
  } finally {
    setIsLoading(false);
  }
};

  return (
    <Container component="main" maxWidth="xs">
      <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">
          Create a New Profile
        </Typography>
        <Box component="form" onSubmit={handleRegister} sx={{ mt: 3 }}>
          <TextField 
            margin="normal" 
            required 
            fullWidth 
            id="username" 
            label="Username" 
            name="username" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            autoFocus
          />
          <TextField 
            margin="normal" 
            required 
            fullWidth 
            name="password" 
            label="Master Password" 
            type="password" 
            id="password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
          />
          <Button 
            type="submit" 
            fullWidth 
            variant="contained" 
            sx={{ mt: 3, mb: 2 }} 
            disabled={isLoading}
          >
            {isLoading ? 'Creating Profile...' : 'Create Profile'}
          </Button>
          <MuiLink component={NextLink} href="/" variant="body2" sx={{ textAlign: 'center', display: 'block' }}>
            {"Already have a profile? Sign in"}
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