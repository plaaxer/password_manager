// src/app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box, Button, Container, Typography, IconButton, List, ListItem, ListItemText,
  CircularProgress, Stack, TextField, Paper, Divider, Snackbar, Alert,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon, Visibility as ViewIcon } from '@mui/icons-material';
import api from '@/services/api';
import AddPasswordModal from '@/components/AddPasswordModal';
import UpdatePasswordModal from '@/components/UpdatePasswordModal';
import ViewPasswordModal from '@/components/ViewPasswordModal';

interface PasswordMetadata {
  service_name: string;
  username: string;
}

export default function DashboardPage() {
  const [passwords, setPasswords] = useState<PasswordMetadata[]>([]);
  const [masterPassword, setMasterPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [selectedService, setSelectedService] = useState<PasswordMetadata | null>(null);
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isUpdateOpen, setIsUpdateOpen] = useState(false);
  const [isViewOpen, setIsViewOpen] = useState(false);
  
  const router = useRouter();

  useEffect(() => {
    if (!localStorage.getItem('accessToken')) router.push('/');
    else setIsAuthenticated(true);
  }, [router]);

  const fetchPasswords = async () => {
    if (!masterPassword) {
      setNotification({ type: 'error', message: "Please enter your master password." });
      return;
    }
    setIsLoading(true);
    try {
      const response = await api.get('/passwords', { data: { master_password: masterPassword } });
      setPasswords(response.data);
    } catch (error) {
      setNotification({ type: 'error', message: "Failed to fetch passwords. Check master password." });
      setPasswords([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (serviceName: string) => {
    if (confirm(`Delete password for ${serviceName}?`)) {
      try {
        await api.delete(`/passwords/${serviceName}`);
        setNotification({ type: 'success', message: 'Password deleted.' });
        fetchPasswords();
      } catch (error) {
        setNotification({ type: 'error', message: 'Deletion failed.' });
      }
    }
  };
  
  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    router.push('/');
  };

  if (!isAuthenticated) {
    return <Container sx={{ display: 'flex', justifyContent: 'center', mt: '20vh' }}><CircularProgress /></Container>;
  }

  return (
    <>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Stack spacing={4}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h4" component="h1">Password Manager</Typography>
            <Button variant="outlined" color="error" onClick={handleLogout}>Logout</Button>
          </Box>

          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Unlock Passwords</Typography>
            <Stack direction="row" spacing={2}>
              <TextField fullWidth type="password" label="Master Password" size="small" value={masterPassword} onChange={(e) => setMasterPassword(e.target.value)} />
              <Button variant="contained" onClick={fetchPasswords} disabled={isLoading}>
                {isLoading ? <CircularProgress size={24} /> : 'List Services'}
              </Button>
            </Stack>
          </Paper>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5">Your Services</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setIsAddOpen(true)}>
              Add New
            </Button>
          </Box>

          <List>
            {passwords.map((p) => (
              <Paper key={p.service_name} sx={{ mb: 2 }} variant="outlined">
                <ListItem
                  secondaryAction={
                    <Stack direction="row" spacing={1}>
                      <IconButton edge="end" onClick={() => { setSelectedService(p); setIsViewOpen(true); }}><ViewIcon /></IconButton>
                      <IconButton edge="end" onClick={() => { setSelectedService(p); setIsUpdateOpen(true); }}><EditIcon /></IconButton>
                      <IconButton edge="end" onClick={() => handleDelete(p.service_name)}><DeleteIcon color="error" /></IconButton>
                    </Stack>
                  }
                >
                  <ListItemText primary={p.service_name} secondary={p.username} />
                </ListItem>
              </Paper>
            ))}
          </List>
        </Stack>
      </Container>
      
      <AddPasswordModal open={isAddOpen} onClose={() => setIsAddOpen(false)} onSuccess={fetchPasswords} />
      {selectedService && (
        <>
          <UpdatePasswordModal open={isUpdateOpen} onClose={() => setIsUpdateOpen(false)} onSuccess={fetchPasswords} service={selectedService} />
          <ViewPasswordModal open={isViewOpen} onClose={() => setIsViewOpen(false)} serviceName={selectedService.service_name} />
        </>
      )}
      <Snackbar open={!!notification} autoHideDuration={6000} onClose={() => setNotification(null)}>
        <Alert onClose={() => setNotification(null)} severity={notification?.type} sx={{ width: '100%' }}>
          {notification?.message}
        </Alert>
      </Snackbar>
    </>
  );
}