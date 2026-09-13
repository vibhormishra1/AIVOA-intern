import {createSlice,createAsyncThunk} from '@reduxjs/toolkit'; import {listComplaints} from '../../api/complaintApi';
export const fetchComplaints=createAsyncThunk('dashboard/fetch',async()=> (await listComplaints()).data);
export default createSlice({name:'dashboard',initialState:{items:[],loading:false},extraReducers:b=>b.addCase(fetchComplaints.pending,s=>{s.loading=true}).addCase(fetchComplaints.fulfilled,(s,a)=>{s.items=a.payload;s.loading=false})}).reducer;
