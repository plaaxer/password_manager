// src/components/AddPasswordModal.tsx
import { useState } from 'react';
import {
  Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Stack, Snackbar, Alert
} from '@mui/material';
import api from '@/services/api';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AddPasswordModal({ open, onClose, onSuccess }: Props) {
  const [serviceName, setServiceName] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await api.post('/passwords', { service_name: serviceName, username, password });
      onSuccess();
      onClose();
    } catch (err) {
      setError('Failed to store password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Add New Password</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 2 }}>
          <TextField required label="Service Name" value={serviceName} onChange={(e) => setServiceName(e.target.value)} />
          <TextField required label="Username / Email" value={username} onChange={(e) => setUsername(e.target.value)} />
          <TextField required label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {error && <Alert severity="error">{error}</Alert>}
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isLoading}>
          {isLoading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}