// src/components/AddPasswordModal.tsx
import { useState, useEffect } from 'react';
import {
  Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Stack, Alert
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
  // 1. ADDED STATE FOR MASTER PASSWORD
  const [masterPassword, setMasterPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Clear form when modal opens
  useEffect(() => {
    if (open) {
      setServiceName('');
      setUsername('');
      setPassword('');
      setMasterPassword('');
      setError(null);
    }
  }, [open]);

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 2. ADD master_password TO THE API CALL
      await api.post('/passwords', { 
        service_name: serviceName, 
        username, 
        password,
        master_password: masterPassword
      });
      onSuccess();
      onClose();
    } catch (err) {
      setError('Failed to store password. Check your master password.');
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
          <TextField required label="Password for Service" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          {/* 3. ADDED THE MASTER PASSWORD INPUT FIELD */}
          <TextField required label="Your Master Password" type="password" value={masterPassword} onChange={(e) => setMasterPassword(e.target.value)} helperText="Required to encrypt this new password." />
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
