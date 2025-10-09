// src/components/ViewPasswordModal.tsx
import { useState, useEffect } from 'react';
import {
  Button, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Stack, Alert, Box, Typography
} from '@mui/material';
import api from '@/services/api';

interface Props {
  open: boolean;
  onClose: () => void;
  serviceName: string;
}

export default function ViewPasswordModal({ open, onClose, serviceName }: Props) {
  const [masterPassword, setMasterPassword] = useState('');
  const [retrievedPassword, setRetrievedPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if(open) {
        setMasterPassword('');
        setRetrievedPassword('');
        setError(null);
    }
  }, [open]);

  const handleFetch = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get(`/passwords/${serviceName}`, { data: { master_password: masterPassword } });
      setRetrievedPassword(response.data.password);
    } catch (err) {
      setError('Failed to retrieve password. Check master password.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(retrievedPassword);
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>View Password for {serviceName}</DialogTitle>
      <DialogContent>
        {!retrievedPassword ? (
          <Stack spacing={2} sx={{ mt: 2 }}>
            <TextField required label="Master Password" type="password" value={masterPassword} onChange={(e) => setMasterPassword(e.target.value)} />
            <Button onClick={handleFetch} variant="contained" disabled={isLoading}>
              {isLoading ? 'Decrypting...' : 'View Password'}
            </Button>
            {error && <Alert severity="error">{error}</Alert>}
          </Stack>
        ) : (
          <Box sx={{ mt: 2, p: 2, border: '1px solid grey', borderRadius: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography fontFamily="monospace">{retrievedPassword}</Typography>
            <Button onClick={copyToClipboard} size="small">Copy</Button>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}