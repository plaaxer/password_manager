// src/components/UpdatePasswordModal.tsx
import { useState, useEffect } from 'react';
import {
  Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Stack, Alert
} from '@mui/material';
import api from '@/services/api';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  service: { service_name: string, username: string };
}

export default function UpdatePasswordModal({ open, onClose, onSuccess, service }: Props) {
  const [username, setUsername] = useState(service.username);
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if(open) {
        setUsername(service.username);
        setPassword('');
        setError(null);
    }
  }, [open, service]);

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await api.put(`/passwords/${service.service_name}`, { service_name: service.service_name, username, password });
      onSuccess();
      onClose();
    } catch (err) {
      setError('Failed to update password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Update Password for {service.service_name}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <TextField required label="Username / Email" value={username} onChange={(e) => setUsername(e.target.value)} />
          <TextField required label="New Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <Alert severity="error">{error}</Alert>}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isLoading}>
          {isLoading ? 'Updating...' : 'Update'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}