import axios from 'axios';
const client = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1' });
export const extractComplaint = (payload) => client.post('/complaints/extract', payload);
export const saveComplaint = (payload) => client.post('/complaints', payload);
export const listComplaints = () => client.get('/complaints');
export const chatComplaint = (id, message) => client.post(`/complaints/${id}/chat`, { message });
