import axios from 'axios';
const client = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1' });
export const extractComplaint = (payload) => {
  const formData = new FormData();
  if (payload.file) {
    formData.append('file', payload.file);
    if (payload.file_type) formData.append('file_type', payload.file_type);
  } else if (payload.file_content) {
    formData.append('file_content', payload.file_content);
    formData.append('file_type', payload.file_type || 'txt');
  }
  return client.post('/complaints/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const saveComplaint = (payload) => client.post('/complaints', payload);
export const listComplaints = () => client.get('/complaints');
export const chatComplaint = (id, message) => client.post(`/complaints/${id}/chat`, { message });
